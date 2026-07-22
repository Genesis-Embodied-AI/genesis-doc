# `IPCCoupler`

The `IPCCoupler` uses Incremental Potential Contact (IPC), a barrier-based, intersection-free contact model built on [libuipc](https://github.com/spiriMirror/libuipc). It unifies rigid bodies (handled as affine-body-dynamics objects) and FEM bodies in one contact framework, and is the right choice for cloth and large-deformation soft bodies where robustness matters more than speed. Select it by passing `gs.options.IPCCouplerOptions` to the scene.

## Options

Configures the inter-solver coupler built on Incremental Potential Contact (IPC), including its Newton solver settings. Time step, gravity, and differentiable simulation mode are inherited from `SimOptions` and should not be set here.

```{eval-rst}
.. autoclass:: genesis.options.solvers.IPCCouplerOptions
```

## Configuration

Coupling happens automatically as the scene steps; there is no per-step coupling call. `IPCCouplerOptions` exposes the Newton solver controls (`newton_max_iterations`, `newton_tolerance`), the contact settings (`contact_d_hat`, the barrier activation distance, and `contact_friction_enable`), and the linear-system solver choice. Fields left as `None` fall back to the libuipc defaults (for example `contact_d_hat` defaults to `0.01`). See the Options section above for the full list. For usage, see {doc}`/user_guide/theory/couplers/index`.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
