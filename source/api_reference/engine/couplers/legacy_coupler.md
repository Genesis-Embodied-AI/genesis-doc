# `LegacyCoupler`

The `LegacyCoupler` is the default coupler. It handles every cross-solver pair (rigid, MPM, SPH, PBD, FEM) and is the right choice for general multi-physics scenes. It is slated for deprecation in favor of the SAP and IPC couplers. The scene uses it when you pass no `coupler_options`.

## Options

Configures the legacy inter-solver coupler, which toggles pairwise coupling between the rigid, MPM, SPH, PBD, and FEM solvers.

```{eval-rst}
.. autoclass:: genesis.options.solvers.LegacyCouplerOptions
```

## Configuration

Each field of `LegacyCouplerOptions` is a boolean that enables one solver pair (`rigid_mpm`, `rigid_sph`, `rigid_pbd`, `rigid_fem`, `mpm_sph`, `mpm_pbd`, `fem_mpm`, `fem_sph`), all `True` by default. See the Options section above for the full list. For usage, see {doc}`/user_guide/theory/couplers/index`.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
