# Device & Platform Utilities

Functions for detecting and configuring the compute platform and device.

## Platform Detection

```python
import genesis as gs

# Get platform before init
platform = gs.get_platform()
print(platform)  # "Linux", "macOS", or "Windows"

# After init, access global
gs.init()
print(gs.platform)  # Same result
```

## Device Information

```python
import genesis as gs

gs.init(backend=gs.gpu)

# Get PyTorch device
device = gs.device
print(device)  # cuda:0, mps:0, cpu, etc.

# Get active backend
backend = gs.backend
print(backend)  # gs.cuda, gs.metal, gs.cpu, etc.
```

## Backend Selection

### Automatic Selection

```python
# GPU auto-selects based on platform
gs.init(backend=gs.gpu)
# Linux -> CUDA
# macOS -> Metal
```

### Manual Selection

```python
# Force specific backend
gs.init(backend=gs.cuda)    # NVIDIA CUDA
gs.init(backend=gs.metal)   # Apple Metal
gs.init(backend=gs.cpu)     # CPU fallback
```

## Random Seed

```python
import genesis as gs

# Set random seed for reproducibility
gs.init(seed=42)

# Or set later
gs.set_random_seed(42)
```

## Global Variables

After `gs.init()`, these are available:

| Variable | Type | Description |
|----------|------|-------------|
| `gs.platform` | str | Platform: "Linux", "macOS", "Windows" |
| `gs.device` | torch.device | PyTorch device for tensors |
| `gs.backend` | gs.backend | Active compute backend |
| `gs.EPS` | float | Numerical epsilon (e.g., 1e-15) |

## Type Hints

```python
# Quadrants types
gs.qd_float  # Quadrants float type
gs.qd_int    # Quadrants int type
gs.qd_vec3   # Quadrants 3D vector
gs.qd_mat3   # Quadrants 3x3 matrix

# PyTorch types
gs.tc_float  # PyTorch float dtype
gs.tc_int    # PyTorch int dtype
```

## See Also

- {doc}`constants` - Backend enums
- {doc}`tensor_utils` - Tensor operations
