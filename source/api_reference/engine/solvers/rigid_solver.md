# RigidSolver

The `RigidSolver` handles rigid body dynamics, including articulated bodies, robots, and rigid objects. For usage, see {doc}`/user_guide/physics/rigid_bodies`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.RigidOptions
```

### Option enums

The values accepted by the `RigidOptions` fields above. The model each one selects is described in
{doc}`/user_guide/theory/rigid_solver/constraints`.

```{eval-rst}
.. autoclass:: genesis.constants.integrator()
.. autoclass:: genesis.constants.constraint_solver()
.. autoclass:: genesis.constants.friction_cone()
.. autoclass:: genesis.constants.contact_resolution()
.. autoclass:: genesis.constants.broadphase_traversal()
```

## RigidSolver

```{eval-rst}
.. autoclass:: genesis.engine.solvers.rigid.rigid_solver.RigidSolver
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/api_reference/engine/entity/rigid_entity/index`: RigidEntity.
