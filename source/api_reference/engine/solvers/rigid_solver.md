# `RigidSolver`

The `RigidSolver` handles rigid body dynamics, including articulated bodies, robots, and rigid objects.

## Overview

The RigidSolver implements:

- **Forward dynamics:** compute accelerations from forces and torques.
- **Collision detection:** GJK and MPR support-function methods, with optimized primitive paths.
- **Contact and constraint resolution:** iterative constraint solving (CG or Newton).
- **Joint constraints:** revolute, prismatic, ball, and free joints.
- **Articulated bodies:** multi-body tree structures loaded from URDF or MJCF.

For usage, see {doc}`/user_guide/physics/rigid_bodies`.

## Collision detection

The RigidSolver uses support-function collision detection with optimized fallbacks:

- **MPR (Minkowski Portal Refinement):** the default narrow-phase method.
- **GJK (Gilbert–Johnson–Keerthi):** more stable but slower; enabled through `use_gjk_collision` and used by default in differentiable mode.
- **Primitives:** optimized paths for sphere, box, and capsule collisions.

## Constraint solving

Contacts and joint constraints are resolved by an iterative solver. Two solvers are available through `constraint_solver`: `gs.constraint_solver.CG` and `gs.constraint_solver.Newton`. See {doc}`/api_reference/engine/solvers/rigid_options` for the tuning parameters.

## See also

- {doc}`/api_reference/entity/rigid_entity/index`: RigidEntity.
- {doc}`/api_reference/engine/solvers/rigid_options`: full options.
