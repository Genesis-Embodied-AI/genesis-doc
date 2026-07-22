# Tensor utilities

Genesis World provides utilities for converting between different array and tensor formats.

## Overview

Genesis World uses:
- **Quadrants fields**: For GPU-accelerated physics computation
- **PyTorch tensors**: For state access and differentiability
- **NumPy arrays**: For data export and visualization

## Conversion helpers

The helpers below are exposed under `gs.utils`. They accept Genesis, PyTorch, or array-like inputs and handle any GPU-to-CPU transfer internally.

```python
# Convert a tensor to a NumPy array (handles GPU transfer; pass dtype= to set the output dtype)
arr = gs.utils.tensor_to_array(tensor)

# Move a tensor to CPU, leaving its dtype unchanged
cpu_tensor = gs.utils.tensor_to_cpu(tensor)

# Wrap array-like data as a Genesis tensor on the configured device and default dtype
tensor = gs.utils.to_gs_tensor([1.0, 2.0, 3.0])
```

State getters such as `robot.get_qpos()` already return tensors on `gs.device`; setters such as `robot.set_dofs_position(...)` accept array-like inputs directly and broadcast scalars across dofs.

## Data types

| Genesis World | PyTorch | NumPy | Description |
|---------|---------|-------|-------------|
| `gs.tc_float` | `torch.float32` | `np.float32` | Default float |
| `gs.tc_int` | `torch.int32` | `np.int32` | Default int |

## See also

- {doc}`device`: Device configuration
- {doc}`/api_reference/engine/states/index`: State management
