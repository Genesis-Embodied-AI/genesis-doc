# Tensor utilities

Genesis World provides utilities for converting between array and tensor formats.

## Overview

Genesis World keeps simulation data in three formats:

- **Quadrants fields:** GPU-accelerated physics computation.
- **PyTorch tensors:** state access and differentiability.
- **NumPy arrays:** data export and visualization.

## Conversion helpers

The helpers below are exposed under `gs.utils`. They accept Genesis, PyTorch, or array-like inputs and handle any GPU-to-CPU transfer internally.

```{eval-rst}
.. autofunction:: genesis.utils.misc.tensor_to_array
.. autofunction:: genesis.utils.misc.tensor_to_cpu
.. autofunction:: genesis.utils.misc.to_gs_tensor
.. autofunction:: genesis.utils.misc.assert_gs_tensor
```

## See also

- {doc}`device`: the precision-dependent dtype aliases (`gs.tc_float`, `gs.np_float`, `gs.qd_float`, and their integer counterparts), and the globals `gs.init()` sets.
- {doc}`/api_reference/engine/states/index`: state management.
