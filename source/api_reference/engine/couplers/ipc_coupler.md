# `IPCCoupler`

The `IPCCoupler` uses Incremental Potential Contact (IPC), a barrier-based, intersection-free contact model built on [libuipc](https://github.com/spiriMirror/libuipc). It unifies rigid bodies (handled as affine-body-dynamics objects) and FEM bodies in one contact framework, and is the right choice for cloth and large-deformation soft bodies where robustness matters more than speed. Select it by passing `gs.options.IPCCouplerOptions` to the scene.

## Minimal example

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        contact_d_hat=0.01,  # barrier activation distance, meters
    ),
)
```

Coupling then happens automatically as the scene steps; there is no per-step coupling call.

## Configuration

`IPCCouplerOptions` exposes the Newton solver controls (`newton_max_iterations`, `newton_tolerance`), the contact settings (`contact_d_hat`, the barrier activation distance, and `contact_friction_enable`), and the linear-system solver choice. Fields left as `None` fall back to the libuipc defaults (for example `contact_d_hat` defaults to `0.01`). See {doc}`/api_reference/engine/couplers/ipc_coupler_options` for the full list.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
- {doc}`/api_reference/engine/couplers/ipc_coupler_options`: IPC coupler options.
