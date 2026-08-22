# Utilities and helpers

Genesis World bundles a set of helper modules under `genesis.utils` for the operations that surround a simulation: selecting a compute backend, converting between array formats, applying geometric transforms, and loading assets from disk. Each linked page documents one of them in detail.

## Modules

- **{doc}`device`:** detecting the platform and selecting the compute backend and PyTorch device.
- **{doc}`tensor_utils`:** converting between Quadrants fields, PyTorch tensors, and NumPy arrays.
- **{doc}`geom`:** quaternion, rotation, and coordinate-transform helpers in `genesis.utils.geom`.
- **{doc}`mesh`:** loading meshes, generating primitives, and tetrahedralizing solids in `genesis.utils.mesh`.
- **{doc}`file_io`:** cache and source directory paths, plus loading URDF and MJCF descriptions.
- **{doc}`tools`:** timing loops and saving media in `genesis.utils.tools`.

## Initialization

Most utilities assume the library has been initialized. `gs.init()` selects the backend, sets the random seed and the float precision, and publishes the resolved configuration as module-level globals:

```python
import genesis as gs

gs.init(
    backend=gs.gpu,  # first available of CUDA, ROCm, Metal
    precision="32",
    seed=42,
)
```

{doc}`device` covers the backend resolution, the globals it sets (`gs.device`, `gs.backend`, `gs.EPS`), and the precision-dependent dtype aliases.

## Components

```{toctree}
:titlesonly:

device
tensor_utils
geom
mesh
file_io
tools
```

## See also

- {doc}`/api_reference/options/index`: the options classes that configure a scene, including the Pydantic base class every one inherits.
