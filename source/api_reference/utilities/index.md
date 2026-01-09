# Utilities & Helpers

Genesis provides various utility functions, constants, and helper classes for common operations.

## Overview

This section covers:

- **Constants**: Enums for joint types, geometry types, backends
- **Device utilities**: Platform detection, device selection
- **Tensor utilities**: Array/tensor conversions
- **Geometry utilities**: Transform operations
- **File I/O**: Path utilities, URDF/MJCF parsing

## Quick Reference

### Initialization

```python
import genesis as gs

# Initialize with default settings
gs.init()

# Initialize with specific backend
gs.init(backend=gs.cpu)      # CPU backend
gs.init(backend=gs.gpu)      # GPU backend (CUDA/Metal)

# With custom settings
gs.init(
    seed=42,              # Random seed
    precision="32",       # Float precision
    debug=False,          # Debug mode
    backend=gs.gpu,
)
```

### Global Variables

After `gs.init()`, these globals are available:

| Variable | Description |
|----------|-------------|
| `gs.platform` | Platform string ("Linux", "macOS", etc.) |
| `gs.device` | PyTorch device |
| `gs.backend` | Active backend enum |
| `gs.EPS` | Numerical epsilon |

## Components

```{toctree}
:titlesonly:

constants
device
tensor_utils
geometry
file_io
```

## See Also

- {doc}`/api_reference/options/index` - Configuration options
