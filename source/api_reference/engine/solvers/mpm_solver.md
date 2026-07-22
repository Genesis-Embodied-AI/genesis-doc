# MPMSolver

The `MPMSolver` implements the Material Point Method (MPM) for simulating a wide range of materials including elastic solids, granular materials, fluids, and phase transitions. It combines Lagrangian particles that track material points with a background Eulerian grid that solves the momentum equations, transferring between them with MLS-MPM for stability. The materials it supports are listed in {doc}`/api_reference/engine/material/mpm/index`. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.MPMOptions
```

## See also

- {doc}`/api_reference/engine/entity/mpm_entity`: MPMEntity.
- {doc}`/api_reference/engine/material/mpm/index`: MPM materials.
