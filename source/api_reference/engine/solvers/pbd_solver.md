# PBDSolver

The `PBDSolver` implements Position Based Dynamics for simulating cloth, soft bodies, and particle systems with fast, stable steps. It simulates the entities built from the PBD entity options; see {doc}`/api_reference/engine/entity/pbd_entity/index`. For the algorithm, its constraint groups, and usage, see {doc}`/user_guide/theory/soft_solvers` and {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.PBDOptions
```

## PBDSolver

```{eval-rst}
.. autoclass:: genesis.engine.solvers.pbd_solver.PBDSolver
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/api_reference/engine/entity/pbd_entity/index`: PBD entities.
- {doc}`/api_reference/engine/entity/pbd_entity/index`: the PBD entity options and the materials they accept.
