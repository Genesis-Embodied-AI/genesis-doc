# SAPCoupler

The `SAPCoupler` (Sweep and Prune) provides efficient spatial acceleration for multi-physics coupling.

## Overview

The SAP coupler:

- Uses sweep-and-prune for broad-phase collision
- Efficient for large numbers of objects
- Reduces narrow-phase checks

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

## See Also

- {doc}`index` - Coupler overview
- {doc}`ipc_coupler` - IPC coupling
