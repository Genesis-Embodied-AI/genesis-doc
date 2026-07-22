# IPCCoupler

The `IPCCoupler` uses Incremental Potential Contact (IPC), a barrier-based, intersection-free contact model built on [libuipc](https://github.com/spiriMirror/libuipc). It unifies rigid bodies (handled as affine-body-dynamics objects) and FEM bodies in one contact framework, and is the right choice for cloth and large-deformation soft bodies where robustness matters more than speed. Select it by passing `gs.options.IPCCouplerOptions` to the scene.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.IPCCouplerOptions
```

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
