# `RigidSolver`

The `RigidSolver` handles rigid body dynamics, including articulated bodies, robots, and rigid objects.

## Overview

The RigidSolver implements:

- **Forward dynamics:** compute accelerations from forces and torques.
- **Collision detection:** GJK and MPR support-function methods, with optimized primitive paths.
- **Contact and constraint resolution:** iterative constraint solving (CG or Newton).
- **Joint constraints:** revolute, prismatic, ball, and free joints.
- **Articulated bodies:** multi-body tree structures loaded from URDF or MJCF.

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        enable_collision=True,
        enable_joint_limit=True,
        constraint_solver=gs.constraint_solver.Newton,
    ),
)

# Add rigid entities
plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="urdf/franka_panda/panda.urdf"))
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 1), size=(1.0, 1.0, 1.0)))

scene.build()

# Control the robot's dofs
robot.set_dofs_position(target_positions)
robot.set_dofs_velocity(target_velocities)

for i in range(1000):
    scene.step()
```

## Collision detection

The RigidSolver uses support-function collision detection with optimized fallbacks:

- **MPR (Minkowski Portal Refinement):** the default narrow-phase method.
- **GJK (Gilbert–Johnson–Keerthi):** more stable but slower; enabled through `use_gjk_collision` and used by default in differentiable mode.
- **Primitives:** optimized paths for sphere, box, and capsule collisions.

## Constraint solving

Contacts and joint constraints are resolved by an iterative solver. Two solvers are available through `constraint_solver`:

```python
# Use the Newton solver with more iterations for better convergence
rigid_options = gs.options.RigidOptions(
    constraint_solver=gs.constraint_solver.Newton,
    iterations=100,
)
```

## See also

- {doc}`/api_reference/entity/rigid_entity/index`: RigidEntity.
- {doc}`/api_reference/engine/solvers/rigid_options`: full options.
