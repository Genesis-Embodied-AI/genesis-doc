# RigidSolver

The `RigidSolver` handles rigid body dynamics simulation, including articulated bodies, robots, and rigid objects.

## Overview

The RigidSolver implements:

- **Forward dynamics**: Compute accelerations from forces/torques
- **Collision detection**: GJK, MPR, and support function methods
- **Contact resolution**: Impulse-based or iterative constraint solving
- **Joint constraints**: Revolute, prismatic, ball, free joints
- **Articulated bodies**: Multi-body tree structures (URDF, MJCF)

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
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 1)))

scene.build()

# Control robot
robot.set_dofs_position(target_positions)
robot.set_dofs_velocity(target_velocities)

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `RigidOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `enable_collision` | bool | Enable collision detection |
| `enable_joint_limit` | bool | Enforce joint limits |
| `constraint_solver` | enum | Solver type (CG, Newton) |
| `max_contact_per_geom` | int | Maximum contacts per geometry |
| `contact_resolve_eps` | float | Contact resolution tolerance |

## Collision Detection

The RigidSolver supports multiple collision detection methods:

- **GJK (Gilbert-Johnson-Keerthi)**: General convex collision
- **MPR (Minkowski Portal Refinement)**: Penetration depth
- **Primitives**: Optimized sphere, box, capsule collisions

## Contact Resolution

Two main approaches:

1. **Impulse-based**: Direct velocity update
2. **Constraint solving**: Iterative optimization (CG, Newton)

```python
# Use Newton solver for better convergence
rigid_options = gs.options.RigidOptions(
    constraint_solver=gs.constraint_solver.Newton,
    iterations=10,
)
```

## See Also

- {doc}`/api_reference/entity/rigid_entity/index` - RigidEntity
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/rigid_options` - Full options
