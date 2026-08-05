# Control your robot

Without actuation, the arm from {doc}`hello_genesis` falls under gravity. Genesis World has a built-in [PD controller](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller) that takes a target joint position or velocity, and you can also command force directly. This tutorial covers both, plus writing the joint state without going through physics. The complete script is [`examples/tutorials/control_your_robot.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/control_your_robot.py).

## Scene setup

The scene is the same single-arm setup from {doc}`hello_genesis`: a ground plane and a Franka arm loaded from MJCF, simulated at `dt=0.01` s.

```python
gs.init(backend=gs.gpu)

scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0, -3.5, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=30,
    ),
    sim_options=gs.options.SimOptions(
        dt=0.01,
    ),
    show_viewer=True,
)

plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(
        file="xml/franka_emika_panda/panda.xml",
    ),
)
scene.build()
```

Every snippet below issues its control command after the build, to hold or move the arm.

## Joints and degrees of freedom

A **joint** connects two links, and a **dof** (degree of freedom) is one independent coordinate that a joint contributes. On the Franka arm the two line up: 7 revolute arm joints and 2 prismatic gripper joints, each carrying a single dof, make a 9-dof articulated body. Other joint types carry more, so a free joint contributes 6 dofs and a ball joint 3.

The distinction matters because every control method addresses dofs by index, so start by mapping the joint names in the MJCF/URDF file to the dof indices the solver assigned them:

```python
joints_name = (
    "joint1",
    "joint2",
    "joint3",
    "joint4",
    "joint5",
    "joint6",
    "joint7",
    "finger_joint1",
    "finger_joint2",
)
motors_dof_idx = [franka.get_joint(name).dofs_idx_local[0] for name in joints_name]
```

`dofs_idx_local` is the dof index relative to this entity, and each single-dof joint exposes a one-element list, hence the `[0]`. Use `joint.dofs_idx` when you need the dof's global index within the scene.

## Control gains

The controller has two gains: `kp` (stiffness) scales the force by the distance to the target, and `kv` (damping) opposes it in proportion to the current velocity, which keeps the dof from overshooting the target. Genesis World parses both from the MJCF or URDF file when the model provides them, but we recommend setting them explicitly, because gains from another model rarely transfer unchanged. `set_dofs_force_range` caps the controller's output.

```python
franka.set_dofs_kp(
    kp=np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local=motors_dof_idx,
)
franka.set_dofs_kv(
    kv=np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local=motors_dof_idx,
)
franka.set_dofs_force_range(
    lower=np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),  # N*m / N
    upper=np.array([87, 87, 87, 87, 12, 12, 12, 100, 100]),
    dofs_idx_local=motors_dof_idx,
)
```

These methods share the pattern used throughout the control API: a tensor of values paired with the dof indices they apply to, lining up element by element.

## Setting state versus controlling

`set_*` and `control_*` look similar and do different things.

- `set_*` writes the robot state directly, without consulting the dynamics. The dof lands on the requested value in a single step.
- `control_*` sends a target to the controller, which produces forces that move the robot toward it over several steps, respecting the dynamics and the force range set above.

Use `set_dofs_position` to reset an episode or place a robot at a starting configuration, and keep it out of a control loop. On a rigid entity it zeroes the dof velocities as well, so the robot starts from rest; pass `zero_velocity=False` to keep the velocities it had:

```python
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), motors_dof_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), motors_dof_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), motors_dof_idx)
    scene.step()
```

With the viewer on, the arm snaps to a new configuration every 50 steps.

## PD and force control

Switching from `set_*` to the matching `control_*` method turns a state assignment into an actuated command. The controller holds a position target until you replace it, so a single call is enough.

```python
franka.control_dofs_position(
    np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
    motors_dof_idx,
)
```

Different dofs can run under different control modes at the same time, because passing a subset of indices leaves the remaining dofs on their previous command. Here the first dof follows a velocity target while the rest stay under position control:

```python
# control first dof with velocity, and the rest with position
franka.control_dofs_position(
    np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
    motors_dof_idx[1:],
)
franka.control_dofs_velocity(
    np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
    motors_dof_idx[:1],
)
```

`control_dofs_force` applies a torque (or force, for prismatic dofs) directly, skipping the PD controller. Commanding zero force lets gravity take over and the arm falls:

```python
franka.control_dofs_force(
    np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
    motors_dof_idx,
)
```

## Reading forces back

Two accessors report the forces at each dof after a step:

```python
# force applied by the controller
print("control force:", franka.get_dofs_control_force(motors_dof_idx))
# actual force experienced by each dof
print("internal force:", franka.get_dofs_force(motors_dof_idx))
```

`get_dofs_control_force` is what the controller commanded, computed from the target and gains under position or velocity control, and equal to your input under force control. `get_dofs_force` is the total force the dof actually experiences, combining that control force with internal effects such as contact and Coriolis forces.

Running the full example produces this sequence:

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/control_your_robot.mp4" type="video/mp4">
Video: the Franka arm cycling through position, velocity, and force control.
</video>

## Applying external forces

The `control_*` methods act in joint space, through the dofs. Sometimes you want to push or twist a link directly in Cartesian space instead: a thruster, wind, a scripted tug on a payload, or a disturbance to see how a controller recovers. The rigid solver applies such wrenches with `apply_links_external_force` and `apply_links_external_torque`.

An external force lasts for a single step and is then cleared, so reapply it on every step you want it active:

```python
rigid = scene.sim.rigid_solver
hand = franka.get_link("hand").idx

for i in range(150):
    # push the hand straight up with 50 N in the world frame
    rigid.apply_links_external_force(
        force=np.array([[0.0, 0.0, 50.0]]),  # N, shape ([n_envs,] n_links, 3)
        links_idx=[hand],
    )
    scene.step()
```

The force and torque tensors follow the batch convention used throughout the API: shape `([n_envs,] n_links, 3)`, matching `links_idx`, with the leading `n_envs` dimension dropped in a single-environment scene. Forces are in newtons and torques in newton-meters.

Both methods take the same optional arguments:

- **`links_idx`:** which links to act on. `None` targets every link.
- **`envs_idx`:** which environments to act on in a batched scene. `None` targets all of them.
- **`ref`:** the reference frame the wrench is applied at: `"link_origin"` (default), `"link_com"` (the link's center of mass), or `"root_com"` (the center of mass of the whole kinematic tree).
- **`local`:** by default the wrench is expressed in world coordinates. Set `local=True` to express it in the reference frame's own coordinates instead, so the force rotates with the link.

## Pick and place with a suction cup

An industrial suction gripper behaves like an instant rigid grasp, which you can reproduce by welding two rigid bodies together for the duration of the grasp. The rigid solver exposes `add_weld_constraint` and `delete_weld_constraint`, each taking the two link indices to attach or detach. The runnable version is [`examples/rigid/suction_cup.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/suction_cup.py), which moves the end-effector above a cube, welds them, transports the cube, and releases it.

Move to a pose above the cube using {doc}`inverse kinematics </user_guide/robot_control/inverse_kinematics_motion_planning>`, then activate the "suction" by welding the cube's link to the gripper's `hand` link:

```python
# ... arm moved above the cube via inverse_kinematics + control_dofs_position ...
rigid = scene.sim.rigid_solver
link_cube = cube.get_link("box_baselink").idx
link_franka = franka.get_link("hand").idx
rigid.add_weld_constraint(link_cube, link_franka)
```

While the weld is active the cube tracks the gripper, so transporting it is just
more IK targets. Releasing is a single call:

```python
rigid.delete_weld_constraint(link_cube, link_franka)
```

:::{note}
The weld is an ideal rigid attachment: it enforces no compliance or grasp-force
limit. For a physically grounded grasp, control the gripper fingers against the
object instead.
:::

## See also

- {doc}`hello_genesis`: the minimal scene this tutorial builds on.
- {doc}`/user_guide/robot_control/inverse_kinematics_motion_planning`: solving for joint targets from a desired end-effector pose.
- {doc}`/api_reference/engine/entity/index`: the full entity control API.
