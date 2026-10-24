# Tensor utilities

Genesis World provides utilities for converting between array and tensor formats.

## Overview

Genesis World keeps simulation data in three formats:

- **Quadrants fields:** GPU-accelerated physics computation.
- **PyTorch tensors:** state access and differentiability.
- **NumPy arrays:** data export and visualization.

## Conversion helpers

The helpers below are exposed under `gs.utils`. They accept PyTorch tensors or array-like inputs. `tensor_to_cpu` and `tensor_to_array` handle the GPU-to-CPU transfer internally, and `to_gs_tensor` moves the data to `gs.device`.

```{eval-rst}
.. autofunction:: genesis.utils.misc.tensor_to_array
.. autofunction:: genesis.utils.misc.tensor_to_cpu
.. autofunction:: genesis.utils.misc.to_gs_tensor
```

## See also

- {doc}`device`: the precision-dependent dtype aliases (`gs.tc_float`, `gs.np_float`, `gs.qd_float`, and their integer counterparts), and the globals `gs.init()` sets.
- {doc}`/api_reference/engine/states/index`: state management.
