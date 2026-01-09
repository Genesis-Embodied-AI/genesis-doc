# 🔒 Constraints

Genesis supports runtime constraints for manipulation tasks like suction grasping.

## Weld Constraints

Weld constraints rigidly attach two links together (6 DOF constraint).

### Adding a Weld Constraint

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
franka = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
cube = scene.add_entity(gs.morphs.Box(pos=(0.65, 0, 0.02), size=(0.04, 0.04, 0.04)))
scene.build()

# Get link handles
rigid = scene.sim.rigid_solver
end_effector = franka.get_link("hand")
cube_link = cube.base_link

# Create constraint arrays
link_cube = np.array([cube_link.idx], dtype=gs.np_int)
link_franka = np.array([end_effector.idx], dtype=gs.np_int)

# Add weld constraint (suction engages)
rigid.add_weld_constraint(link_cube, link_franka)
```

### Removing a Weld Constraint

```python
# Release object
rigid.delete_weld_constraint(link_cube, link_franka)
```

## Suction Cup Example

```python
# Move to object
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(50):
    scene.step()

# Attach (suction on)
rigid.add_weld_constraint(link_cube, link_franka)

# Lift
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.28]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# Place
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.4, 0.2, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# Release (suction off)
rigid.delete_weld_constraint(link_cube, link_franka)
```

## Multi-Environment Constraints

```python
scene.build(n_envs=4)

# Add constraint to specific environments
rigid.add_weld_constraint(link_cube, link_franka, envs_idx=(0, 1, 2))

# Delete from subset
rigid.delete_weld_constraint(link_cube, link_franka, envs_idx=(0, 1))
```

## Connect Constraints

Connect constraints enforce position-only coincidence (3 DOF), allowing relative rotation.

```xml
<!-- In MJCF/URDF -->
<equality>
    <connect name="ball_joint" body1="link_1" body2="link_2" anchor="0 0 1" />
</equality>
```

## Query Active Constraints

```python
constraints = rigid.get_weld_constraints()
print(constraints)  # Active constraint pairs
```

## Constraint Properties

- **Weld**: Full 6-DOF constraint (translation + rotation)
- **Connect**: 3-DOF constraint (translation only)
- **Instant**: No force limits or compliance
- **Runtime**: Can be added/removed dynamically
