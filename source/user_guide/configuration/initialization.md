# Initialization and backends

Every Genesis World program begins with a single call to `gs.init()`. It selects the compute backend, fixes the numeric precision, seeds the random number generators, and configures logging: the global state that every scene you build afterward relies on. Call it once, before you construct a {py:class}`gs.Scene <genesis.engine.scene.Scene>` or any options object. If you skip it, the first API call raises `GenesisException: Genesis hasn't been initialized. Did you call gs.init()?`.

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.gpu)
```

That is all most programs need: it runs on the GPU if one is available and falls back to the CPU otherwise. `gs.init()` takes only keyword arguments, and the sections below cover the ones that come up in practice.

## Choosing a backend

The `backend` argument selects the device the physics runs on. Pass one of the backend constants:

| Backend | Runs on |
|---|---|
| `gs.gpu` | The best available GPU, with automatic fallback (see below). |
| `gs.cpu` | The CPU. |
| `gs.cuda` | An NVIDIA CUDA GPU. |
| `gs.amdgpu` | An AMD ROCm GPU. |
| `gs.metal` | An Apple Silicon GPU. |

Genesis World resolves `gs.gpu` (and the default `backend=None`) in order, **CUDA → AMD → Metal → CPU**, taking the first one that initializes on your machine, so `gs.gpu` is portable across hardware. With no GPU usable it falls back to the CPU and logs a warning rather than failing.

```python
gs.init(backend=gs.gpu)   # portable: use a GPU if present, else CPU
gs.init(backend=gs.cpu)   # force CPU, e.g. for CI or debugging
```

After initialization, the resolved backend and the underlying PyTorch device are readable on the `gs` module:

```python
gs.init(backend=gs.gpu)
print(gs.backend)  # the backend actually selected, e.g. gs.cuda
print(gs.device)   # the torch.device tensors are placed on
```

:::{note}
`gs.init()` may only be called once per process. Calling it again raises `Genesis already initialized.` Use `gs.destroy()` to tear down the current backend before re-initializing.
:::

## Precision

`precision` chooses the floating-point width used throughout the simulation. It is `"32"` (single precision) by default, and `"64"` selects double precision:

```python
gs.init(backend=gs.gpu, precision="64")
```

Single precision is faster and uses less memory, and double precision buys numerical headroom in stiff or ill-conditioned scenes at a cost in speed. Three details come with the choice:

- **Integer indices are always 32-bit**, regardless of `precision`. Only floating-point values switch.
- **Double precision is not available on Apple Metal.** Requesting `precision="64"` with `backend=gs.metal` raises an error.
- `gs.init()` sets PyTorch's global default dtype and device to match, so tensors you create afterward land on the right device with the right dtype without extra arguments.

{doc}`conventions` covers the dtypes the API returns.

## Reproducibility

Pass `seed` to make a run repeatable. It seeds Python, NumPy, PyTorch, and the Quadrants compiler together:

```python
gs.init(backend=gs.gpu, seed=0)
```

Seeding alone does not guarantee bit-for-bit determinism on a GPU, where some kernels are non-deterministic by default. For fully deterministic runs, add `debug=True`:

```python
gs.init(backend=gs.cpu, seed=0, debug=True)
```

`debug=True` turns on PyTorch's deterministic algorithms, disables cuDNN autotuning, and raises the log level to `DEBUG`. Use it to reproduce a bug or validate a result rather than for a production run, because deterministic kernels are considerably slower, and keep to `gs.cpu` where determinism has to hold: GPU backends support it only partially.

## Deterministic mode

`use_deterministic_algorithms=True` guarantees that a scene replays a rollout identically: reset it, drive it with the same inputs, and every step reproduces the previous run bit-for-bit on a given machine.

```python
gs.init(backend=gs.gpu, use_deterministic_algorithms=True)
```

The mode is opt-in because the guarantee is paid for in throughput. Left off, Genesis is free to decide at runtime how a computation is carried out wherever that buys speed, with nothing requiring the decision to come out the same way twice. Today that freedom is spent picking between implementations: several interchangeable ones of the same computation, each written for a different workload, with every site timing its own candidates as the simulation runs and landing on the one fastest for the state the scene is currently in.

Interchangeable implementations compute the same thing by construction, but agree only to within floating-point noise, and a simulation amplifies such a difference until the two runs have visibly parted ways. Which one ran at which step is therefore part of the trajectory, and nothing about that is reproducible: the timings follow how busy the machine is, and the measurements accumulate across resets, so a rollout also depends on everything the process ran before it. They accumulate on purpose - environments in a training loop reset constantly, often one at a time, and starting the measurements over at every reset would leave them forever measuring instead of exploiting what they measured. Deterministic mode gives up the freedom altogether: every such choice is settled up front, on the option that suits most scenes, and never revisited.

What it costs therefore depends on the scene and on how far its state travels: nothing at all while the settled choice is the one that would have been picked anyway, and up to the gap between the implementations whenever another would have taken over. Measure your own scene before committing to the mode where throughput dominates, policy training in particular; turn it on to compare two runs or to track down a divergence.

The choice can also be made by hand, by pinning one implementation through the Quadrants `QD_PERFDISPATCH_FORCE` environment variable, which removes the measurement just as the mode does and is therefore reproducible on its own. Use it when the implementation deterministic mode settles on is the wrong one for your scene. For the constraint solve, which is where the choice matters most today, the two candidates are:

```bash
# One thread per environment, each solved as a whole; favored when the environment count alone keeps the GPU busy.
QD_PERFDISPATCH_FORCE=func_solve_body:func_solve_body_monolith python my_script.py

# Parallelism inside each environment; favored when too few environments run to keep the GPU busy on their own.
QD_PERFDISPATCH_FORCE=func_solve_body:func_solve_decomposed python my_script.py
```

Note that this is a workaround naming internal implementations: it is no part of the public API, and may change or disappear in any release.

## Logging

`gs.init()` creates the logger and exposes it as `gs.logger`. Control its verbosity with `logging_level`; when unset it defaults to `"info"` (or `"debug"` when `debug=True`).

```python
gs.init(backend=gs.gpu, logging_level="warning")  # quiet: warnings and errors only
```

Set `logger_verbose_time=True` to prefix each log line with a full timestamp instead of the elapsed time alone. The `theme` argument (`"dark"`, `"light"`, or `"dumb"`) controls the terminal color scheme; use `"dumb"` to disable colors in environments that mangle ANSI codes.

## Performance mode

With `performance_mode=True`, the compiler bakes static tensor shapes into its kernels for roughly 30% faster simulation, at the cost of recompiling whenever the scene changes (which can take several minutes). Leave it off for research, debugging, and interactive work; turn it on for policy training and production runs where the scene is fixed.

```python
gs.init(backend=gs.gpu, performance_mode=True)  # fixed scene, maximum throughput
```

## See also

- {doc}`/user_guide/overview/installation`: installing Genesis World and its GPU drivers.
- {doc}`config_system`: configuring the scene itself once initialized.
- {doc}`conventions`: the coordinate, unit, tensor-shape, and dtype conventions the API follows.
- {doc}`/user_guide/getting_started/hello_genesis`: the minimal end-to-end scene.
