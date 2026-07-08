# Inverse kinematics and motion planning

This tutorial builds a complete pick-and-place task with a Franka arm: solve **inverse kinematics** (IK) for a target end-effector pose, plan a collision-free path to that configuration, then close the gripper and lift a cube. Along the way it covers the pose conventions IK expects and why the two control modes (position and force) are used at different stages.

The full runnable script is [`examples/tutorials/IK_motion_planning_grasp.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/IK_motion_planning_grasp.py). This page explains the ideas behind it; run the script to see the arm move.

```{figure} ../../_static/images/IK_mp_grasp.png
:alt: A Franka arm positioned above a small cube on the ground plane, viewed in the Genesis World viewer.
```

Motion planning uses the [OMPL](https://ompl.kavrakilab.org/) library. Install it with the instructions on the {doc}`installation </user_guide/overview/installation>` page before running the example.

## Scene and robot setup

Load a ground plane, a small cube to grasp, and the Franka arm, then build the scene:

```python
cube = scene.add_entity(
    gs.morphs.Box(
        size=(0.04, 0.04, 0.04),
        pos=(0.65, 0.0, 0.02),  # meters, Z-up
    )
)
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
scene.build()
```

The Franka has nine degrees of freedom (**dof**): seven arm joints and two gripper fingers. Splitting them into two index arrays lets you command the arm and the fingers independently:

```python
motors_dof = np.arange(7)
fingers_dof = np.arange(7, 9)
```

Position control is a PD controller, so it needs per-dof stiffness (`kp`) and damping (`kv`) gains, plus a force range. The values below are tuned for the Franka; a different robot needs its own, and a well-authored URDF or MJCF may already provide them.

```python
franka.set_dofs_kp(
    np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
)
franka.set_dofs_kv(
    np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
)
franka.set_dofs_force_range(
    np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    np.array([87, 87, 87, 87, 12, 12, 12, 100, 100]),
)
```

## Solving inverse kinematics

IK answers the question "what joint angles put the end-effector at this pose?" In Genesis World it is a method on the robot entity: name the link that acts as the end-effector, give it a target pose, and it returns a full-body configuration (`qpos`).

```python
end_effector = franka.get_link("hand")

qpos = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.25]),  # world-frame position, meters
    quat=np.array([0, 1, 0, 0]),  # w-x-y-z; 180 deg about X, gripper points down
)
```

The target `pos` and `quat` are in the **world frame**, using the right-handed, Z-up coordinate system and the scalar-first `(w, x, y, z)` quaternion convention. Here `(0, 1, 0, 0)` is a 180-degree rotation about the world X-axis, which orients the gripper to point straight down at the table.

The returned `qpos` covers every dof, including the fingers. Setting the finger entries opens the gripper before the approach:

```python
qpos[-2:] = 0.04  # open gripper, meters per finger
```

## Planning a path to the configuration

IK gives a goal configuration but not how to get there. `plan_path` finds a collision-free trajectory from the current configuration to `qpos_goal` and returns a list of waypoints, one per simulation step:

```python
path = franka.plan_path(
    qpos_goal=qpos,
    num_waypoints=200,  # 200 steps at dt=0.01 s -> 2 s of motion
)

for waypoint in path:
    franka.control_dofs_position(waypoint)
    scene.step()

# let the PD controller settle onto the final waypoint
for i in range(100):
    scene.step()
```

Executing the path steps the simulation once per waypoint. The extra 100 steps at the end matter: position control is a PD controller, so the arm trails its commanded target by a small error. Stepping a little longer lets it converge onto the last waypoint before the next phase begins.

:::{tip}
`scene.draw_debug_path(path, franka)` visualizes the planned trajectory in the viewer, and `scene.clear_debug_object(...)` removes it afterward. The example uses both to render the path while the arm follows it.
:::

## Grasping and lifting

The rest of the task is a sequence of IK solves and control commands. To reach down to the cube, solve IK for a lower target and drive only the arm dofs with position control:

```python
qpos = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.130]),
    quat=np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)  # arm only; leave fingers as-is
for i in range(100):
    scene.step()
```

To grasp, switch the fingers from position control to **force control**. Position control would command a target opening; force control instead applies a steady squeezing force, which holds the cube robustly regardless of its exact width:

```python
franka.control_dofs_position(qpos[:-2], motors_dof)
franka.control_dofs_force(np.array([-0.5, -0.5]), fingers_dof)  # 0.5 N inward per finger
for i in range(100):
    scene.step()
```

Finally, solve IK for a raised target and hold the grasp while the arm lifts:

```python
qpos = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.28]),
    quat=np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(200):
    scene.step()
```

The fingers stay under force control from the grasp step, so the cube rises with the gripper.

## See also

- {doc}`advanced_ik` — multi-target IK, null-space control, and solver tuning
- {doc}`constraints` — weld and connect constraints for locking links together at runtime
- {doc}`path_planning` — collision-free motion planning with RRT
- {doc}`control_your_robot` — position, velocity, and force control in depth
