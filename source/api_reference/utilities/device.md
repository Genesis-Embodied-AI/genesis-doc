# Device and platform utilities

`gs.init()` resolves which compute backend Genesis World runs on and which PyTorch device holds the tensors it hands back, then publishes both as module-level globals.

## Backend selection

Pass `backend=gs.gpu` to take whichever GPU backend the machine has. Genesis World tries CUDA, then ROCm (`gs.amdgpu`), then Metal, then the CPU, and warns when it lands on the CPU because no GPU was available:

```python
import genesis as gs

gs.init(backend=gs.gpu)

print(gs.backend)  # the backend it settled on: gs.cuda, gs.amdgpu, gs.metal, or gs.cpu
print(gs.device)  # the matching PyTorch device: cuda:0, mps:0, or cpu
```

Name a backend instead when a machine has more than one and the choice matters, or to compare a run against the CPU:

```python
gs.init(backend=gs.cuda)  # NVIDIA CUDA
gs.init(backend=gs.metal)  # Apple Metal
gs.init(backend=gs.cpu)  # every platform
```

A named backend that the machine cannot provide raises instead of falling back, so a run meant for the GPU fails at `gs.init()` rather than silently simulating on the CPU.

## Backend

```{eval-rst}
.. autoclass:: genesis.constants.backend()
```

## Functions

```{eval-rst}
.. autofunction:: genesis.utils.misc.get_device
.. autofunction:: genesis.utils.misc.set_random_seed
```

## Globals set by `gs.init()`

| Global | Type | Holds |
|---|---|---|
| `gs.device` | `torch.device` | The PyTorch device every returned tensor lives on (`cuda:0`, `mps:0`, `cpu`). |
| `gs.backend` | `gs.backend` | The backend that was selected, after resolving `gs.gpu`. |
| `gs.EPS` | `float` | Numerical epsilon for the active float precision. |

The `precision` argument decides the float width, and the dtype aliases follow it: `gs.qd_float`, `gs.np_float`, and `gs.tc_float` are the Quadrants, NumPy, and PyTorch float types, resolving to 32-bit under the default `precision="32"` and 64-bit under `precision="64"`. Integer aliases (`gs.qd_int`, `gs.np_int`, `gs.tc_int`) stay 32-bit at either precision. Use the aliases rather than a literal `torch.float32` so a scene keeps working when its precision changes.

## See also

- {doc}`tensor_utils`: converting between Quadrants fields, PyTorch tensors, and NumPy arrays.
- {doc}`/user_guide/configuration/initialization`: what `gs.init()` sets up, and the other arguments it takes.
