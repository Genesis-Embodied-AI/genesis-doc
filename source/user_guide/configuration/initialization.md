# Initialization and backends

Every Genesis World program begins with a single call to `gs.init()`. It selects the compute backend, fixes the numeric precision, seeds the random number generators, and configures logging: the global state that every scene you build afterward relies on. Call it once, before you construct a `gs.Scene` or any options object. If you skip it, the first API call raises `GenesisException: Genesis hasn't been initialized. Did you call gs.init()?`.

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.gpu)
```

That is all most programs need: it runs on the GPU if one is available and falls back to the CPU otherwise. `gs.init()` takes only keyword arguments; the sections below cover the ones you will actually reach for.

## Choosing a backend

The `backend` argument selects the device the physics runs on. Pass one of the backend constants:

| Backend | Runs on |
|---|---|
| `gs.gpu` | The best available GPU, with automatic fallback (see below). |
| `gs.cpu` | The CPU. |
| `gs.cuda` | An NVIDIA CUDA GPU. |
| `gs.amdgpu` | An AMD ROCm GPU. |
| `gs.metal` | An Apple Silicon GPU. |

`gs.gpu` (and the default of `backend=None`) is resolved in order: **CUDA → AMD → Metal → CPU**. Genesis World picks the first one that initializes on your machine, so `gs.gpu` is portable across hardware. If no GPU is usable it falls back to the CPU and logs a warning rather than failing.

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

`precision` chooses the floating-point width used throughout the simulation. It is `"32"` (single precision) by default and can be raised to `"64"` (double precision):

```python
gs.init(backend=gs.gpu, precision="64")
```

Single precision is faster and uses less memory; double precision trades speed for numerical headroom in stiff or ill-conditioned scenes. A few things to keep in mind:

- **Integer indices are always 32-bit**, regardless of `precision`. Only floating-point values switch.
- **Double precision is not available on Apple Metal.** Requesting `precision="64"` with `backend=gs.metal` raises an error.
- `gs.init()` sets PyTorch's global default dtype and device to match, so tensors you create afterward land on the right device with the right dtype without extra arguments.

What dtype the tensors returned by the API carry is described in {doc}`conventions`.

## Reproducibility

Pass `seed` to make a run repeatable. It seeds Python, NumPy, PyTorch, and the Quadrants compiler together:

```python
gs.init(backend=gs.gpu, seed=0)
```

Seeding alone does not guarantee bit-for-bit determinism on a GPU, where some kernels are non-deterministic by default. For fully deterministic runs, add `debug=True`:

```python
gs.init(backend=gs.cpu, seed=0, debug=True)
```

`debug=True` turns on PyTorch's deterministic algorithms, disables cuDNN autotuning, and raises the log level to `DEBUG`. It is meant for reproducing bugs and validating results, not for production: it **dramatically reduces runtime speed**, and it is only partially supported on GPU backends (deterministic execution is most reliable on `gs.cpu`).

## Logging

The logger is created during `gs.init()` and exposed as `gs.logger`. Control its verbosity with `logging_level`; when unset it defaults to `"info"` (or `"debug"` when `debug=True`).

```python
gs.init(backend=gs.gpu, logging_level="warning")  # quiet: warnings and errors only
```

Set `logger_verbose_time=True` to prefix each log line with a full timestamp instead of just the elapsed time. The `theme` argument (`"dark"`, `"light"`, or `"dumb"`) controls the terminal color scheme; use `"dumb"` to disable colors in environments that mangle ANSI codes.

## Environment variables

A few environment variables adjust backend and runtime behavior without changing your code, which is useful for CI, containers, and quick experiments:

| Variable | Effect |
|---|---|
| `QD_ENABLE_<BACKEND>=0` | Skip a backend during `gs.gpu` resolution, e.g. `QD_ENABLE_METAL=0`. |
| `GS_TORCH_FORCE_CPU_DEVICE=1` | Keep PyTorch tensors on the CPU even when the physics runs on a GPU. |
| `QD_NUM_THREADS=N` | Cap the CPU thread and compile-thread count (defaults to 1 on CPU). |
| `GS_ENABLE_NDARRAY=0` | Force static array mode in the compiler backend. |
| `GS_ENABLE_ZEROCOPY=0/1` | Force zero-copy tensor sharing between PyTorch and the backend off or on. |

For relocating the compilation caches (a separate concern, relevant to benchmarking), see {doc}`/user_guide/developers/profiling`.

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
