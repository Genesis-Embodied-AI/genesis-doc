# Utilities and helpers

Genesis World bundles a set of helper modules under `genesis.utils` for the operations that surround a simulation: selecting a compute backend, converting between array formats, applying geometric transforms, and loading assets from disk. This page is the entry point to those modules; each linked page documents one of them in detail.

## Modules

- **{doc}`constants`:** enums and named constants for compute backends, joint types, and geometry types.
- **{doc}`device`:** detecting the platform and selecting the compute backend and PyTorch device.
- **{doc}`tensor_utils`:** converting between Quadrants fields, PyTorch tensors, and NumPy arrays.
- **{doc}`geom`:** quaternion, rotation, and coordinate-transform helpers in `genesis.utils.geom`.
- **{doc}`mesh`:** loading meshes, generating primitives, and tetrahedralizing solids in `genesis.utils.mesh`.
- **{doc}`file_io`:** cache and source directory paths, plus loading URDF and MJCF descriptions.
- **{doc}`tools`:** timing loops and saving media in `genesis.utils.tools`.

## Initialization and globals

Most utilities assume the library has been initialized. `gs.init()` selects the backend, sets the random seed and float precision, and populates the module-level globals below.

```python
import genesis as gs

gs.init(
    backend=gs.gpu,  # CUDA on Linux, Metal on macOS
    precision="32",
    seed=42,
)
```

After `gs.init()` returns, these globals hold the resolved configuration:

| Global | Type | Description |
|---|---|---|
| `gs.device` | `torch.device` | The active PyTorch device (for example, `cuda:0`, `mps:0`, or `cpu`). |
| `gs.backend` | backend enum | The backend that was actually selected, after resolving `gs.gpu`. |
| `gs.EPS` | `float` | Numerical epsilon for the active float precision. |

## Components

```{toctree}
:titlesonly:

constants
device
tensor_utils
geom
mesh
file_io
tools
```

## See also

- {doc}`/api_reference/options/index`: the options classes that configure a scene, including the Pydantic base class every one inherits.
