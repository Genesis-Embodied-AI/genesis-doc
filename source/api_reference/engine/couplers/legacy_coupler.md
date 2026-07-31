# LegacyCoupler

The `LegacyCoupler` is the default coupler. It handles every cross-solver pair (rigid, MPM, SPH, PBD, FEM) and is the right choice for general multi-physics scenes. It is slated for deprecation in favor of the SAP and IPC couplers. The scene uses it when you pass no `coupler_options`.

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
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
