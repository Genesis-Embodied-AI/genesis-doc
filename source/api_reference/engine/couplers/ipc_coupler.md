# IPCCoupler

The `IPCCoupler` (Incremental Potential Contact) provides robust contact handling for multi-physics scenarios.

## Overview

IPC coupling:

- Variational contact formulation
- Guaranteed intersection-free trajectories
- Robust for challenging contact scenarios
- Higher computational cost

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        d_hat=0.001,  # Contact distance threshold
    ),
)
```

## When to Use IPC

- Complex deformable-deformable contact
- Scenarios requiring intersection-free guarantees
- When stability is more important than speed

## See Also

- {doc}`index` - Coupler overview
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/coupler_options` - Coupler options
