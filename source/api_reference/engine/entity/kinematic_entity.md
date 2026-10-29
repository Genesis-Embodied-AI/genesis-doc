# KinematicEntity

A `KinematicEntity` is a ghost or reference entity: the kinematic solver computes its forward kinematics for rendering, and it takes no part in contacts or dynamics. Build one with `gs.options.KinematicEntityOptions`, for example to show a target pose next to a simulated robot.

## Options

```{eval-rst}
.. autoclass:: genesis.options.entities.KinematicEntityOptions
```

## KinematicEntity

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_entity.KinematicEntity
    :members:
    :undoc-members:
    :show-inheritance:
```
