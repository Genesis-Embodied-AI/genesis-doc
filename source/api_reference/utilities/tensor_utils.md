# Tensor Utilities

Genesis provides utilities for converting between different array and tensor formats.

## Overview

Genesis uses:
- **Taichi fields**: For GPU-accelerated physics computation
- **PyTorch tensors**: For state access and differentiability
- **NumPy arrays**: For data export and visualization

## Tensor Conversion

### To NumPy

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Get state as NumPy array
qpos = robot.get_qpos()
qpos_np = gs.utils.tensor_to_array(qpos)
print(type(qpos_np))  # numpy.ndarray
```

### To CPU

```python
# Move tensor to CPU (if on GPU)
qpos_cpu = gs.utils.tensor_to_cpu(qpos)
```

### Creating Tensors

```python
import torch

# Create tensor on correct device
tensor = torch.zeros(10, device=gs.device, dtype=gs.tc_float)

# Or use Genesis wrapper
tensor = gs.utils.to_gs_tensor([1.0, 2.0, 3.0])
```

## Common Patterns

### Getting Entity State

```python
# Returns PyTorch tensor
positions = robot.get_qpos()
velocities = robot.get_qvel()

# Convert to NumPy for processing
import numpy as np
pos_np = positions.cpu().numpy()
```

### Setting Entity State

```python
import torch

# From NumPy
target = np.array([0.1, 0.2, 0.3])
robot.set_dofs_position(torch.from_numpy(target).to(gs.device))

# From list
robot.set_dofs_position([0.1, 0.2, 0.3])
```

### Batched Tensors

With `n_envs > 1`:

```python
scene.build(n_envs=16)

# Batched output: (n_envs, n_dofs)
all_positions = robot.get_qpos()

# Select specific environments
some_positions = robot.get_qpos(envs_idx=[0, 5, 10])
```

## Data Types

| Genesis | PyTorch | NumPy | Description |
|---------|---------|-------|-------------|
| `gs.tc_float` | `torch.float32` | `np.float32` | Default float |
| `gs.tc_int` | `torch.int32` | `np.int32` | Default int |

## See Also

- {doc}`device` - Device configuration
- {doc}`/api_reference/engine/states/index` - State management
