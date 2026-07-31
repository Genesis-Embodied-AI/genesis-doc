# KinematicSolver

The `KinematicSolver` is a lightweight solver for ghost or reference entities that only computes forward kinematics for visualization. It performs no collision detection, physics integration, or constraint solving, so its entities move exactly as scripted without interacting with the rest of the scene. An entity uses it when built with the `gs.materials.Kinematic` material.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.KinematicOptions
```

## KinematicSolver

```{eval-rst}
.. autoclass:: genesis.engine.solvers.kinematic_solver.KinematicSolver
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/api_reference/engine/material/kinematic`: the kinematic material that selects this solver.
