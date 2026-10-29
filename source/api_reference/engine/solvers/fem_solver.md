# FEMSolver

The `FEMSolver` implements the Finite Element Method for simulating deformable solids on tetrahedral meshes. It supports several constitutive models (linear, stable Neo-Hookean, linear corotated), handles large deformations, and integrates explicitly unless `use_implicit_solver` selects the implicit solver, which stays stable at larger time steps. It simulates the entities built from `gs.options.FEMEntityOptions`; see {doc}`/api_reference/engine/entity/fem_entity`. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies` and, for muscle-driven bodies, {doc}`/user_guide/physics/soft_robots`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.FEMOptions
```

## FEMSolver

```{eval-rst}
.. autoclass:: genesis.engine.solvers.fem_solver.FEMSolver
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/api_reference/engine/entity/fem_entity`: FEMEntity.
- {doc}`/api_reference/engine/entity/fem_entity`: the FEM entity options and the materials they accept.
