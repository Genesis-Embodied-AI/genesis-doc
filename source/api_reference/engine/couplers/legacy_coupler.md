# LegacyCoupler

The `LegacyCoupler` is the default: a scene that names no `coupler_options` gets it. It handles every cross-solver pair (rigid, MPM, SPH, PBD, FEM), which suits general multi-physics scenes. It is slated for deprecation in favor of the SAP and IPC couplers.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.LegacyCouplerOptions
```

## LegacyCoupler

```{eval-rst}
.. autoclass:: genesis.engine.couplers.legacy_coupler.LegacyCoupler
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/coupling/index`: the theory behind each coupler.
