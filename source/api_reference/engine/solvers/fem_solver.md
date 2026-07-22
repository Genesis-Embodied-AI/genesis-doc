# FEMSolver

The `FEMSolver` implements the Finite Element Method for simulating deformable solids on tetrahedral meshes. It supports several constitutive models (linear, stable Neo-Hookean, linear corotated), handles large deformations, and offers an explicit integrator by default with an optional implicit solver for stability at larger time steps. The materials it supports are listed in {doc}`/api_reference/engine/material/fem/index`. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies` and, for muscle-driven bodies, {doc}`/user_guide/physics/soft_robots`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.FEMOptions
```

## See also

- {doc}`/api_reference/engine/entity/fem_entity`: FEMEntity.
- {doc}`/api_reference/engine/material/fem/index`: FEM materials.
