# Tensor utilities

Genesis World has helpers for converting between array and tensor formats.

## Overview

Genesis World keeps simulation data in three formats:

- **Quadrants fields:** GPU-accelerated physics computation.
- **PyTorch tensors:** state access and differentiability.
- **NumPy arrays:** data export and visualization.

## Conversion helpers

`gs.utils` exposes the helpers below. They accept Genesis, PyTorch, or array-like inputs and handle any GPU-to-CPU transfer internally.

```{eval-rst}
.. autofunction:: genesis.utils.misc.tensor_to_array
.. autofunction:: genesis.utils.misc.tensor_to_cpu
.. autofunction:: genesis.utils.misc.to_gs_tensor
.. autofunction:: genesis.utils.misc.assert_gs_tensor
```

## Data types

{doc}`device` covers the precision-dependent dtype aliases (`gs.tc_float`, `gs.np_float`, `gs.qd_float`, and their integer counterparts) and how the `precision` argument resolves them.

## See also

- {doc}`device`: device configuration.
- {doc}`/api_reference/engine/states/index`: state management.
