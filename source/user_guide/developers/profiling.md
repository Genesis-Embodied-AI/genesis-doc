# Profiling simulation performance

This page covers how to measure where a Genesis World simulation spends its time. There are three questions worth asking, in order of increasing depth:

- **Throughput:** how many steps per second does the whole scene run? This is the headline number, reported as FPS.
- **Launch latency:** is the GPU actually busy, or is the CPU stalling between kernel launches? This is what limits large parallel simulations that are not yet GPU-bound.
- **Per-kernel time:** which solver kernels dominate a step? This tells you what to optimize.

The first is built in and always available. The other two use the PyTorch profiler, which works even in a simulation that never touches PyTorch.

## Benchmark against a disposable cache

Before you measure anything, get the compilation cache out of the way. Genesis World compiles GPU kernels just-in-time and caches the results to a persistent local folder, so repeated runs of the same scene start quickly. Quadrants, the compiler, keeps its own cache in the same way. This is what you want for day-to-day work, but it distorts profiling and benchmarking: the first run pays the compilation cost and later runs read from the warm cache.

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

Three numbers, all reported per window of wall-clock time:

- **Total FPS:** steps per second summed across every environment. This is the throughput figure to compare against benchmarks.
- **Per-env FPS:** the total divided by the number of environments. Useful when comparing scenes with different batch sizes.
- **Environments:** the value of `n_envs` passed to `scene.build()`. It is omitted when the scene has no batch dimension.

The rate is measured over fixed wall-clock windows and lightly smoothed with an exponential moving average, so it settles to a stable value rather than jumping every step.

### Configuring the counter

The counter is controlled by {py:class}`gs.options.ProfilingOptions <genesis.options.profiling.ProfilingOptions>`, passed to the scene:

```python
scene = gs.Scene(
    profiling_options=gs.options.ProfilingOptions(
        show_FPS=True,       # print the step rate each window; default True
        FPS_tracker_alpha=0.95,  # EMA momentum for the smoothed rate
    ),
)
```

- **`show_FPS`:** whether to print the rate at all. Set it to `False` for quiet runs, or when the log lines interfere with your own output.
- **`FPS_tracker_alpha`:** the smoothing momentum, between 0 and 1. Higher values react more slowly and read more steadily; lower values track sudden changes in speed more closely.

The scene exposes the live options as `scene.profiling_options`, so you can toggle the counter after construction:

```python
scene.profiling_options.show_FPS = False
```

See {doc}`/user_guide/configuration/config_system` for how `ProfilingOptions` fits alongside the other options objects.

## Measuring throughput

The scripts in [`examples/speed_benchmark`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/speed_benchmark) are the reference for measuring throughput on your own hardware. They are the source of truth for a clean benchmark setup; the excerpts below only highlight the choices that matter.

[`examples/speed_benchmark/franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/franka.py) runs a Franka arm across tens of thousands of environments:

```python
gs.init(backend=gs.gpu, performance_mode=True)

scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(dt=0.01),
    show_viewer=False,
)
# ... add plane and franka ...

scene.build(n_envs=30000, env_spacing=(1.0, 1.0))
```

Three choices make this a throughput benchmark rather than an interactive session:

- **`performance_mode=True`** bakes static tensor shapes into the compiled kernels for faster stepping, at the cost of recompiling whenever the scene changes. It is worth it for a fixed benchmark or a training run, not for iterative development.
- **`show_viewer=False`** runs headless. Rendering a window caps throughput at display rates and defeats the purpose.
- **A large `n_envs`** keeps the GPU saturated. Throughput scales with the batch until you run out of VRAM.

[`examples/speed_benchmark/anymal_c.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/anymal_c.py) is the equivalent for a legged robot. For the reasoning behind these settings and other ways to raise throughput, see {doc}`/user_guide/getting_started/parallel_simulation` and {doc}`/user_guide/policy_training/best_practices/efficient_environment`.

## Timing GPU kernels with the PyTorch profiler

The FPS counter tells you *how fast*, not *why*. To see individual GPU kernels and the gaps between them, attach the PyTorch profiler around the steps you care about. It records CUDA activity whether or not your simulation uses PyTorch tensors.

[`examples/speed_benchmark/timers.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/timers.py) wraps a fixed number of steps in a profiler:

```python
with torch.profiler.profile(
    on_trace_ready=torch.profiler.tensorboard_trace_handler("./benchmark"),
    schedule=torch.profiler.schedule(wait=0, warmup=0, active=1),
    record_shapes=False,
    profile_memory=False,
    with_stack=True,
    with_flops=False,
):
    for step in range(500):
        scene.step()
```

The `schedule` selects which steps to record so you can skip the ones you do not care about. Its phases are:

- **`wait`:** steps to ignore at the start, past any one-time initialization.
- **`warmup`:** steps to run while the profiler primes itself but discards the trace.
- **`active`:** steps actually recorded. One is usually enough and keeps memory low.

When you use a multi-phase schedule, advance it by calling `profiler.step()` once per iteration so the profiler knows which phase it is in. See the [PyTorch profiler schedule documentation](https://docs.pytorch.org/docs/stable/profiler.html#torch.profiler.schedule) for details. The resulting trace opens in [TensorBoard](https://www.tensorflow.org/tensorboard) or, if you export a Chrome trace, in [Perfetto](https://ui.perfetto.dev/).

### Reading the trace

On the GPU timeline you get the precise duration of every kernel launch. White gaps between kernels are launch overhead: the GPU sitting idle while the CPU catches up. On a large parallel simulation those gaps should be negligible; if they dominate, the simulation is CPU-bound and no amount of extra environments will help until the stalls are removed. Diagnosing and removing these stalls is the subject of {doc}`/user_guide/policy_training/best_practices/efficient_environment`.

The GPU timeline has no call hierarchy of its own, so it can be hard to tell which Python-side operation a kernel belongs to. Insert a synchronization before each step to force that alignment:

```python
qd.sync()  # block until all Quadrants GPU work completes, so the CPU and GPU timelines line up
scene.step()
```

:::{warning}
Synchronizing every step serializes the CPU and GPU and can roughly halve throughput. Use it to understand a trace, then remove it before measuring speed.
:::

## Per-solver kernel timings

To go below CUDA kernels and time blocks of work inside the rigid solver, [`examples/speed_benchmark/timers.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/speed_benchmark/timers.py) reads the constraint solver's `timers` array and plots per-environment timings in the terminal:

```python
from genesis.utils.misc import qd_to_torch

timers = qd_to_torch(scene.rigid_solver.constraint_solver.constraint_state.timers)
```

Run it with `--profiling` to attach the PyTorch profiler instead, or without to collect and plot the per-solver timings. This reaches into solver internals and is aimed at contributors optimizing the physics kernels rather than at typical simulation code.

## See also

- {doc}`/user_guide/getting_started/parallel_simulation`: scaling to many environments for throughput.
- {doc}`/user_guide/policy_training/best_practices/efficient_environment`: removing CPU–GPU stalls in a training loop.
- {doc}`/user_guide/configuration/config_system`: how `ProfilingOptions` fits with the other options objects.
