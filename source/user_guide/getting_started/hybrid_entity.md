# 🔗 Hybrid Entity

HybridEntity combines rigid and soft body physics for simulating deformable robots with rigid skeletons.

## Overview

A hybrid entity couples:
- **Rigid component**: Skeleton/structure (from URDF)
- **Soft component**: Deformable skin (MPM-based)

Use cases: soft grippers, deformable robots, compliant manipulators.

## Creating a Hybrid Entity

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=3e-3, substeps=10),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(0, 0, -0.2),
        upper_bound=(1, 1, 1),
    ),
)

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="robot.urdf",
        pos=(0.5, 0.5, 0.3),
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.05,
        damping=1000.0,
    ),
)

scene.build()
```

## Hybrid Material Options

```python
gs.materials.Hybrid(
    material_rigid=gs.materials.Rigid(),     # Rigid body material
    material_soft=gs.materials.MPM.Muscle(), # Soft material (MPM only)
    thickness=0.05,                          # Soft skin thickness
    damping=1000.0,                          # Velocity damping
    soft_dv_coef=0.01,                       # Rigid→soft velocity transfer
)
```

## Control

Control uses the rigid skeleton's DOFs:

```python
import numpy as np

for step in range(1000):
    # Sinusoidal joint control
    target_vel = [np.sin(step * 0.01)] * robot.n_dofs
    robot.control_dofs_velocity(target_vel)
    scene.step()
```

## Accessing Components

```python
robot.part_rigid   # RigidEntity (skeleton)
robot.part_soft    # MPMEntity (skin)
robot.n_dofs       # Number of DOFs

# State access
robot.get_dofs_position()
robot.get_dofs_velocity()
```

## Example: Soft Gripper

```python
gripper = scene.add_entity(
    morph=gs.morphs.URDF(file="gripper.urdf", fixed=True),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.02,
        damping=100.0,
    ),
)

# Add object to grasp
ball = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.5, 0.5, 0.1), radius=0.05),
)

scene.build()

# Close gripper
for step in range(500):
    gripper.control_dofs_position([0.5] * gripper.n_dofs)
    scene.step()
```

## From Mesh (Automatic Skeletonization)

Create hybrid entity from arbitrary mesh:

```python
creature = scene.add_entity(
    morph=gs.morphs.Mesh(file="creature.obj", scale=0.1),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(),
        material_soft=gs.materials.MPM.Muscle(E=1e4),
    ),
)
```

Genesis automatically:
1. Extracts skeleton from mesh via skeletonization
2. Creates rigid body from skeleton
3. Maps soft particles to skeleton links

## Notes

- Soft material must be MPM-based (`gs.materials.MPM.*`)
- Higher `damping` reduces oscillation
- Requires `mpm_options` with appropriate bounds
