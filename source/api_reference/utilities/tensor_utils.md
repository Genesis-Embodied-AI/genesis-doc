# Tensor utilities

Genesis World provides utilities for converting between different array and tensor formats.

## Overview

Genesis World uses:
- **Quadrants fields**: For GPU-accelerated physics computation
- **PyTorch tensors**: For state access and differentiability
- **NumPy arrays**: For data export and visualization

## Conversion helpers

The helpers below are exposed under `gs.utils`. They accept Genesis, PyTorch, or array-like inputs and handle any GPU-to-CPU transfer internally.

```{eval-rst}
.. autofunction:: genesis.utils.misc.tensor_to_array
.. autofunction:: genesis.utils.misc.tensor_to_cpu
.. autofunction:: genesis.utils.misc.to_gs_tensor
.. autofunction:: genesis.utils.misc.assert_gs_tensor
```

## Data types

| Genesis World | PyTorch | NumPy | Description |
|---------|---------|-------|-------------|
| `gs.tc_float` | `torch.float32` | `np.float32` | Default float |
| `gs.tc_int` | `torch.int32` | `np.int32` | Default int |

## See also

- {doc}`device`: Device configuration
- {doc}`/api_reference/engine/states/index`: State management
