# Profiling simulation performance

This page covers how to measure where a Genesis World simulation spends its time, through four questions of increasing depth:

- **Throughput:** how many steps per second does the whole scene run? This is the headline number, reported as FPS.
- **Step breakdown:** how much of a step goes to the physics, and how much to the sensors, the viewer, and the recorders around it? The answer tells you whether to optimize the physics at all.
- **Launch latency:** is the GPU actually busy, or is the CPU stalling between kernel launches? This is what limits large parallel simulations that are not yet GPU-bound.
- **Per-kernel time:** which solver kernels dominate a step, and which blocks of code inside them? This tells you what to optimize.

The first two are built in and always available. The other two use the PyTorch profiler, which works even in a simulation that never touches PyTorch, and the cycle counter of Quadrants for timing code inside a kernel.

## Benchmark against a disposable cache

Before you measure anything, get the compilation cache out of the way. Genesis World compiles GPU kernels just-in-time and caches the results to a persistent local folder, so repeated runs of the same scene start quickly. Quadrants, the compiler, keeps its own cache in the same way. This is what you want for day-to-day work, but it distorts profiling and benchmarking: the first run compiles the kernels, and later runs read them from the warm cache.

Do not wipe the persistent cache to get around this. Its effect outlives your experiment, and every future simulation is slow until the cache rebuilds. Instead, redirect both caches to a throwaway directory for the duration of a single run, by setting a few environment variables:

```bash
XDG_CACHE_HOME="$(mktemp -d)" \
GS_CACHE_FILE_PATH="$XDG_CACHE_HOME/genesis" \
QD_OFFLINE_CACHE_FILE_PATH="$XDG_CACHE_HOME/quadrants" \
python your_script.py
```

- `GS_CACHE_FILE_PATH`: Genesis World's cache directory.
- `QD_OFFLINE_CACHE_FILE_PATH`: the Quadrants compiler cache directory.
- `XDG_CACHE_HOME`: the base cache directory, honored on Linux only.

On Linux, `XDG_CACHE_HOME` alone is enough to relocate the Genesis World cache. On Windows and macOS it is ignored, so set `GS_CACHE_FILE_PATH` and `QD_OFFLINE_CACHE_FILE_PATH` explicitly as shown above.

## Reading the FPS counter

By default, Genesis World prints the achieved step rate to the terminal as the simulation runs. The output looks like this:

```text
Running at 43,000,000.00 FPS (1,433.33 FPS per env, 30000 envs).
```

Three numbers, all smoothed over the latest steps:

- **Total FPS:** steps per second summed across every environment. This is the throughput figure to compare against benchmarks.
- **Per-env FPS:** the total divided by the number of environments. Useful when comparing scenes with different batch sizes.
- **Environments:** the value of `n_envs` passed to `scene.build()`. It is omitted when the scene has no batch dimension.

Genesis World measures the period from the start of one step to the start of the next, so the time your own code spends between two calls to `scene.step()` counts, and smooths it with an exponential moving average over samples of 50 ms of stepping each, so the rate settles to a stable value whatever the step rate. A line prints with each sample.

### Configuring the counter

The counter is controlled by {py:class}`gs.options.ProfilingOptions <genesis.options.profiling.ProfilingOptions>`, passed to the scene:

```python
scene = gs.Scene(
    profiling_options=gs.options.ProfilingOptions(
        show_FPS=True,       # print the smoothed step rate; default True
        FPS_tracker_alpha=0.95,  # EMA momentum for the smoothed rate
    ),
)
```

- **`show_FPS`:** whether to print the rate at all. Set it to `False` for quiet runs, or when the log lines interfere with your own output.
- **`FPS_tracker_alpha`:** the smoothing momentum, between 0 and 1. Higher values react more slowly and read more steadily; lower values track sudden changes in speed more closely.

The scene exposes the live options as `scene.options.profiling`, so you can toggle the counter after construction:

```python
scene.options.profiling.show_FPS = False
```

See {doc}`/user_guide/configuration/config_system` for how `ProfilingOptions` fits alongside the other options objects.

## Reading the step breakdown

The FPS counter reports the rate of the whole loop, which includes everything the scene does around the physics and your own code between steps. To see where that time goes, read `scene.timings` after stepping. It maps each phase of the latest step to its wall time in seconds:

| Phase | Covers |
|---|---|
| `physics` | the solvers advancing the state over the substeps |
| `sensors` | the sensor updates, with `sensors/<class name>` giving the share of each sensor class |
| `rendering` | the viewer refresh |
| `recorders` | the recorders reading the state |
| `video` | the cameras rendering and encoding a frame of a recording |
| `step` | the whole call to `scene.step()`, the pre-step callbacks included |
| `period` | the wall time from the start of the previous step to the start of this one, your own code between the two included, so its inverse is the rate the loop achieves |

A phase the step skips is absent from the mapping, for instance `rendering` after `scene.step(update_visualizer=False)`, and the first step has no `period`. The mapping stays empty until the first `scene.step()` returns. A step a pre-step callback vetoes, such as a paused viewer, leaves the timings of the previous step as they are, since the simulation does not advance, and the `period` of the next step counts from the start of the last step that advanced. Resetting the scene or restoring a checkpoint leaves the timings as they are.

Each reading covers the latest step alone, so it jitters from step to step. Smooth a quantity you read every step with a {py:class}`RunningMean <genesis.utils.tools.RunningMean>`, over a window of steps or as an exponential moving average. Invert a phase to read it as a rate, for instance the step rate of the physics without the sensors, rendering, and recording around it:

```python
from genesis.utils.tools import RunningMean

physics_time = RunningMean(window=100)  # mean over the latest 100 steps, NaN until 100 steps have run
for _ in range(1000):
    scene.step()
    physics_time.update(scene.timings["physics"])
physics_fps = 1.0 / physics_time.value  # steps per second of the physics alone
```

[`examples/rigid/hibernation.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/hibernation.py) plots this rate live against the number of awake bodies while a pile of objects settles.

:::{warning}
On a GPU backend, a phase measures the host time spent launching its kernels while the device runs them asynchronously, so the phases add up to the real step only on the CPU backend. `step` is accurate on every backend as long as something in the step reads data back from the device, which makes the host wait for it.
:::

## Measuring throughput

The scripts in [`examples/speed_benchmark`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/speed_benchmark) are the source of truth for a clean benchmark setup on your own hardware, so the excerpts below only highlight the choices that matter.

[`examples/speed_benchmark/franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/franka.py) runs a Franka arm across tens of thousands of environments:

```python
gs.init(backend=gs.gpu, performance_mode=True)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),
    show_viewer=False,
)
# ... add plane and franka ...

scene.build(n_envs=30000, env_spacing=(1.0, 1.0))
```

Three choices make this a throughput benchmark rather than an interactive session:

- **`performance_mode=True`** bakes static tensor shapes into the compiled kernels for faster stepping, at the cost of recompiling whenever the scene changes. Use it for a fixed benchmark or a training run, and leave it off while you iterate.
- **`show_viewer=False`** runs headless. Rendering a window caps throughput at display rates and defeats the purpose.
- **A large `n_envs`** keeps the GPU saturated. Throughput scales with the batch until you run out of VRAM.

[`examples/speed_benchmark/anymal_c.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/anymal_c.py) is the equivalent for a legged robot. For the reasoning behind these settings and other ways to raise throughput, see {doc}`/user_guide/getting_started/parallel_simulation` and {doc}`/user_guide/policy_training/best_practices/efficient_environment`.

## Timing GPU kernels with the PyTorch profiler

The FPS counter tells you *how fast*, not *why*. To see individual GPU kernels and the gaps between them, attach the PyTorch profiler around the steps you care about. It records CPU and CUDA activity whether or not your simulation uses PyTorch tensors.

The profiler takes a schedule that picks which steps to record, so that one-time initialization and the first, compiling steps stay out of the trace. Advance it with `profiler.step()` once per simulation step, and export the trace once the context manager has closed:

```python
from torch.profiler import ProfilerActivity, profile, schedule

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    schedule=schedule(wait=80, warmup=3, active=1, repeat=1),  # tune to your own scene
    record_shapes=False,
    profile_memory=False,
    with_stack=True,
    with_flops=False,
) as profiler:
    for _ in range(100):
        scene.step()
        profiler.step()
profiler.export_chrome_trace("trace.json")
```

The schedule phases are counted in calls to `profiler.step()`, so call it at least `wait + warmup + active` times:

- **`wait`:** steps to skip at the start, long enough to get past everything you do not want to look at.
- **`warmup`:** steps the profiler runs while it primes itself, with the trace discarded.
- **`active`:** steps actually recorded. One is usually enough and keeps memory low.
- **`repeat`:** how many times to run the cycle. Leave it at 1 to record once and stop.

The values above are a starting point rather than a recommendation, so adjust them to your scene; the [PyTorch profiler schedule documentation](https://docs.pytorch.org/docs/stable/profiler.html#torch.profiler.schedule) covers the rest. Open `trace.json` in [Perfetto](https://ui.perfetto.dev/). [`examples/speed_benchmark/timers.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/timers.py) shows the other common output, a trace written for [TensorBoard](https://www.tensorflow.org/tensorboard) through `on_trace_ready=torch.profiler.tensorboard_trace_handler("./benchmark")`.

For the CPU side alone, a sampling profiler such as [py-spy](https://github.com/benfred/py-spy) gives a similar flame graph. The PyTorch profiler has two advantages here: the schedule keeps initialization out of the trace and records the same steps on every run, so timings compare from one run to the next, and it records the actual sequence of calls rather than a statistical sample of them.

### Reading the trace

On the GPU timeline you get the precise start and duration of every kernel launch. White gaps between kernels are launch overhead: the GPU sitting idle while the CPU catches up. On a large parallel simulation those gaps should be negligible; if they dominate, the simulation is CPU-bound and no amount of extra environments will help until the stalls are removed. Diagnosing and removing these stalls is the subject of {doc}`/user_guide/policy_training/best_practices/efficient_environment`.

The GPU timeline has no call hierarchy of its own, so it can be hard to tell which Python-side operation a kernel belongs to. Insert a synchronization before each step to force that alignment:

```python
qd.sync()  # block until all Quadrants GPU work completes, so the CPU and GPU timelines line up
scene.step()
profiler.step()
```

:::{warning}
Synchronizing every step serializes the CPU and GPU and can roughly halve throughput. Use it to understand a trace, then remove it before measuring speed.
:::

## Timing code inside a kernel

The PyTorch profiler times whole CUDA kernels, which is already one level deeper than a CPU profiler plus a synchronization can go. It cannot see inside a kernel, though, and a single Quadrants kernel often runs several stages, such as the line search, the gradient update and the constraint update of the rigid solver. To time those stages separately, per environment, read the hardware cycle counter with `qd.clock_counter()` around each block and write the difference to a buffer.

The rigid constraint solver keeps such a buffer for this purpose, `scene.rigid_solver.constraint_solver.constraint_state.timers`, of shape `(10, n_envs)`: one row per timer, one column per environment. The solver ships without any instrumentation, so the buffer stays at zero until you add some. Start with an enum naming the rows, so that the kernel and the script reading the results agree on them:

```python
from enum import IntEnum


class Time(IntEnum):
    Solve = 0
    LineSearch = 1
    UpdateGradient = 2
```

Then, inside the kernel loop over environments, take a reading before and after each block you want to measure. For instance, to time the whole constraint solve of each environment in `_kernel_solve_monolith` (`genesis/engine/solvers/rigid/constraint/solver.py`):

```python
for i_b in range(_B):
    start = qd.clock_counter()
    # ... the existing body of the loop ...
    constraint_state.timers[Time.Solve, i_b] = qd.clock_counter() - start
```

To time consecutive blocks, such as `Time.LineSearch` and `Time.UpdateGradient` inside an iteration, reuse the end reading of one block as the start of the next.

The counter returns raw cycles, not seconds, so compare readings with each other rather than reading them as durations. On CUDA it counts the cycles of the streaming multiprocessor running the thread, and its rate follows the GPU clock, which boosts and throttles. `qd.clock_freq_hz()` gives the nominal clock rate of the GPU, from which you can derive an approximate duration. On Metal the counter always reads 0, and the buffer holds 32-bit integers instead of 64-bit ones.

[`examples/speed_benchmark/timers.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/timers.py) reads the buffer after each step and plots row 0 per environment in the terminal, which works on a remote server without a display:

```python
from genesis.utils.misc import qd_to_torch

timers = qd_to_torch(scene.rigid_solver.constraint_solver.constraint_state.timers)
```

Run it without arguments to collect and plot the timings, or with `--profiling` to attach the PyTorch profiler instead. Add a label to its `TIMER_LABELS` for each extra row you fill. Instrumenting the solver means editing its kernels, so this is aimed at contributors optimizing the physics rather than at typical simulation code.

## See also

- {doc}`/user_guide/getting_started/parallel_simulation`: scaling to many environments for throughput.
- {doc}`/user_guide/policy_training/best_practices/efficient_environment`: removing CPU–GPU stalls in a training loop.
- {doc}`/user_guide/configuration/config_system`: how `ProfilingOptions` fits with the other options objects.
