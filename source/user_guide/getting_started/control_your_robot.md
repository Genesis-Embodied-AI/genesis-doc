# 🕹️ Control Your Robot

Now that we have loaded an robot, let's go through a comprehensive example to show you how you can control your robot via various ways.

As usual, let's import genesis, create a scene, and load a franka robot:
```python
import numpy as np
import genesis as gs

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        max_FPS       = 60,
    ),
    show_viewer = True,
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)

# when loading an entity, you can specify its pose in the morph.
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (1.0, 1.0, 0.0),
        euler = (0, 0, 0),
    ),
)

########################## build ##########################
scene.build()
```

This robot arm will fall down due to gravity, if we don't give it any actuation force. Genesis has a built-in PD controller ([proportional–integral–derivative controller](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller) ) that takes as input target joint position or velocity. You can also directly set torque/force applied to each joint.

In the context of robotic simulation, `joint` and `dof` (degree-of-freedom) are two related but different concepts. Since we are dealing with a Franka arm, which has 7 revolute joints in the arm and 2 prismatic joints in its gripper, all the joints have 1 dof only, leading to a 9-dof articulated body. In a more general case, there will be joint types such as free joint (6 dofs) or ball joint (3 dofs) that have more than one degrees of freedom. In general, you can think of each dof as a motor and can be controlled independently.

In order to know which joint (dof) to control, we need to map the joint names we (as a user) defined in the URDF/MJCF file to the actual dof index inside the simulator:

```
jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]
```
Note that here we are using `.dof_idx_local` to obtain the local idx of the dof with respect to the robot entity itself. You can also use `joint.dof_idx` to access each joint's global dof index in the scene.

Next, we can set the control gains for each dof. These gains determine how big the actual control force will be, given a target joint position or velocity. Usually, these information will be parsed from the imported MJCF or URDF file, but it's always recommended to tune it manually or refer to a well-tuned value online.

```python
############ Optional: set control gains ############
# set positional gains
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# set velocity gains
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# set force range for safety
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
```
Note that these APIs in general takes as input two sets of values: the actual value to be set, and the corresponding dofs indices. Most control-related APIs follow this convention.

Next, instead of using a physically-realistic PD controller, let's first see how we can manually set the configuration of the robot. These APIs can make sudden changes to the robot state without obeying physics:

```python
# Hard reset
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()
```
If you have viewer turned on, you will see the robot changes state every 50 steps.

Next, let's try to control the robot using the built in PD controller. The API design in Genesis follows a structured pattern. We used `set_dofs_position` to hard set the dofs position. Now we simply changed `set_*` to `control_*` to use the controller counterpart APIs. Here we illustrate different ways for controlling the robot:
```python
# PD control
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # control first dof with velocity, and the rest with position
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # This is the control force computed based on the given control command
    # If using force control, it's the same as the given control command
    print('control force:', franka.get_dofs_control_force(dofs_idx))

    # This is the actual force experienced by the dof
    print('internal force:', franka.get_dofs_force(dofs_idx))

    scene.step()
```
Let's dive into it a bit:
- from step 0 to 500, we are using position control to control all the dofs, and move the robot to 3 target positions sequentially. Note that for `control_*` APIs, once a target value is set, it will be stored internally and you don't need to send repetitive commands to the simulation in the following steps as long as your target stays the same.
- at step 750, we demonstrate we can do hybrid control for different dofs: for the first dof (dof 0), we send a velocity command, while the rest still follows position control commands
- at step 1000, we switch to torque (force) control and send a zero-force command to all the dofs, and the robot will again fall onto the floor due to gravity.

At the end of each step, we print two types of forces: `get_dofs_control_force()` and `get_dofs_force()`.
- `get_dofs_control_force()` returns the force applied by the controller. In case of position or velocity control, this is computed using the target command and the control gains. In case of force (torque) control, this is same as the input control command
- `get_dofs_force()` returns the actual force experience by each dof, this is a combination of the force applied by the controller, and other internal forces such as collision force and coriolis force.

If everything goes right, this is what you should see:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/control_your_robot.mp4" type="video/mp4">
</video>


Here is the full code script covering everything discussed above:
```python
import numpy as np

import genesis as gs

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        res           = (960, 640),
        max_FPS       = 60,
    ),
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    show_viewer = True,
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
    ),
)
########################## build ##########################
scene.build()

jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]

############ Optional: set control gains ############
# set positional gains
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# set velocity gains
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# set force range for safety
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
# Hard reset
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()

# PD control
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # control first dof with velocity, and the rest with position
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # This is the control force computed based on the given control command
    # If using force control, it's the same as the given control command
    print('control force:', franka.get_dofs_control_force(dofs_idx))

    # This is the actual force experienced by the dof
    print('internal force:', franka.get_dofs_force(dofs_idx))

    scene.step()
```

## Pick & Place with a Suction Cup

In many industrial settings robots pick objects using a suction pad that behaves like an "instant" rigid grasp.  In Genesis you can reproduce the same behaviour by temporarily welding two rigid bodies together.

The *rigid solver* inside the scene gives you direct access to this functionality through
`add_weld_constraint()` and `delete_weld_constraint()`.  The API takes two numpy arrays that list the
link indices to be attached / detached.

Below is a minimal example that moves the Franka end-effector above a small cube, welds the two bodies together (imitating suction), transports the cube to another pose and finally releases it again.

```python
import numpy as np
import genesis as gs

# --- (scene and robot creation omitted, identical to the sections above) ---

# Retrieve some commonly used handles
rigid        = scene.sim.rigid_solver          # low-level rigid body solver
end_effector = franka.get_link("hand")        # Franka gripper frame
cube_link    = cube.get_link("box_baselink")   # the link we want to pick

################ Reach pre-grasp pose ################
q_pregrasp = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.13]),  # just above the cube
    quat = np.array([0, 1, 0, 0]),        # down-facing orientation
)
franka.control_dofs_position(q_pregrasp[:-2], np.arange(7))  # arm joints only
for _ in range(50):
    scene.step()

################ Attach (activate suction) ################
link_cube   = np.array([cube_link.idx],   dtype=gs.np_int)
link_franka = np.array([end_effector.idx], dtype=gs.np_int)
rigid.add_weld_constraint(link_cube, link_franka)

################ Lift and transport ################
q_lift = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.28]),  # lift up
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(q_lift[:-2], np.arange(7))
for _ in range(50):
    scene.step()

q_place = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.4, 0.2, 0.18]),  # target place pose
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(q_place[:-2], np.arange(7))
for _ in range(100):
    scene.step()

################ Detach (release suction) ################
rigid.delete_weld_constraint(link_cube, link_franka)
for _ in range(400):
    scene.step()
```

A few remarks:
1. The suction pad is modelled as an *ideal* weld — no compliance or force limit is enforced.  If you need a more physical behaviour you can instead create a `gs.constraints.DampedSpring` or control the gripper fingers.
2. Link indices are **scene-global**, therefore we wrap them in a single-element numpy array to satisfy the API contract.
3. You can attach or detach multiple objects at once by passing arrays with more than one index.

With just two lines of code you can now pick and place arbitrary objects with suction!  Feel free to integrate this snippet into your own control pipeline.
