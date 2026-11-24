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

Genesis World resolves `gs.gpu` (and the default `backend=None`) in order, **CUDA → AMD → Metal → CPU**, taking the first one that initializes on your machine, so `gs.gpu` is portable across hardware. With no GPU usable, `gs.gpu` falls back to the CPU and logs a warning rather than failing. With `debug=True`, the default `backend=None` selects the CPU.

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
- `gs.init()` does not change PyTorch's global default dtype and device. Tensors you create yourself need `dtype=gs.tc_float` and `device=gs.device` to match the simulation.

{doc}`conventions` covers the dtypes the API returns.

## Reproducibility

Pass `seed` to make a run repeatable. It seeds Python, NumPy, PyTorch, and the Quadrants compiler together:

```python
gs.init(backend=gs.gpu, seed=0)
```

Seeding together with {ref}`deterministic mode <deterministic-mode>`, on by default, makes runs repeatable. To debug with bit-exact runs on the CPU, add `debug=True`:

```python
gs.init(backend=gs.cpu, seed=0, debug=True)
```

`debug=True` turns on PyTorch's deterministic algorithms, disables cuDNN autotuning, and raises the log level to `DEBUG`. Use it to reproduce a bug or validate a result rather than for a production run, because deterministic kernels are considerably slower, and keep to `gs.cpu` where determinism has to hold: GPU backends support it only partially.

(deterministic-mode)=
## Deterministic mode

`use_deterministic_algorithms=True` guarantees that a scene replays a rollout identically: reset it, drive it with the same inputs, and every step reproduces the previous run bit-for-bit on a given machine.

```python
gs.init(backend=gs.gpu, use_deterministic_algorithms=True)
```

The default, `use_deterministic_algorithms=None`, enables the mode unless kernels use static arrays, that is with `performance_mode=True` or the `GS_ENABLE_NDARRAY=0` environment variable, in which case it stays off. Pass `False` or `True` to override it either way. The guarantee is paid for in throughput, which is why performance mode leaves it off. Left off, Genesis World may pick at runtime between implementations of the same computation that agree only to within floating-point noise, so two runs drift apart. What the mode costs depends on the scene: where throughput dominates, policy training in particular, measure your scene with `use_deterministic_algorithms=False` before deciding to keep the mode, and keep it on to compare two runs or to track down a divergence.

## Logging

`gs.init()` creates the logger and exposes it as `gs.logger`. Control its verbosity with `logging_level`; when unset it defaults to `"info"` (or `"debug"` when `debug=True`).

```python
gs.init(backend=gs.gpu, logging_level="warning")  # quiet: warnings and errors only
```

Set `logger_verbose_time=True` to prefix each log line with a full timestamp instead of the elapsed time alone. The `theme` argument (`"dark"`, `"light"`, or `"raw"`) controls how log lines are printed: `"dark"` and `"light"` color them for a terminal of that background, and `"raw"` prints plain, compact lines with no colors, banner box or emojis, for log files, continuous integration and coding agents.

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
