# 🧗 Advanced and Parallel IK

The IK solver in Genesis has a lot of powerful features. In this example, we will show how you can configure your IK solver to accept more flexible target pose, and how you can solve for robots in a batched setting.

### IK with multiple end-effector links

In this example, we will use the left and right fingers of the robot gripper as two separate target links. In addition, instead of using a full 6-DoF pose as the target pose for each link, we only solve considering their positions and direction of the z-axis.

```python
import numpy as np
import genesis as gs
import genesis.utils.geom as gu

########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos    = (2.0, -2, 1.5),
        camera_lookat = (0.0, 0.0, 0.0),
        camera_fov    = 40,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit = False,
        enable_collision   = False,
    ),
    show_viewer=True,
)

########################## entities ##########################

scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## build ##########################
scene.build()

# Create debug frames for IK target visualization
target_quat = np.array([0, 1, 0, 0])
T_init = gu.trans_quat_to_T(np.zeros(3), target_quat)
target_left_frame = scene.draw_debug_frame(T_init, axis_length=0.1, origin_size=0.01, axis_radius=0.005)
target_right_frame = scene.draw_debug_frame(T_init, axis_length=0.1, origin_size=0.01, axis_radius=0.005)

center = np.array([0.4, -0.2, 0.25])
r = 0.1

left_finger = robot.get_link('left_finger')
right_finger = robot.get_link('right_finger')

for i in range(0, 2000):
    target_pos_left = center + np.array([np.cos(i/360*np.pi), np.sin(i/360*np.pi), 0]) * r
    target_pos_right = target_pos_left + np.array([0.0, 0.03, 0])

    # Update debug frame positions
    T_left = gu.trans_quat_to_T(target_pos_left, target_quat)
    T_right = gu.trans_quat_to_T(target_pos_right, target_quat)
    scene.update_debug_objects((target_left_frame, target_right_frame), (T_left, T_right))

    q = robot.inverse_kinematics_multilink(
        links    = [left_finger, right_finger],
        poss     = [target_pos_left, target_pos_right],
        quats    = [target_quat, target_quat],
        rot_mask = [False, False, True], # only restrict direction of z-axis
    )

    # Note that this IK is for visualization purposes, so here we do not call scene.step(), but only update the state and the visualizer
    # In actual control applications, you should instead use robot.control_dofs_position() and scene.step()
    robot.set_dofs_position(q)
    scene.visualizer.update()
```

This is what you will see:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/ik_multilink.mp4" type="video/mp4">
</video>

Here are a few new things we hope you could learn in this example:
- We used `robot.inverse_kinematics_multilink()` API for solving IK considering multiple target links. When using this API, we pass in a list of target link objects, a list of target positions, and a list of target orientations (quats).
- We used `rot_mask` to mask out directions of the axes we don't care. In this example, we want both fingers to point downward, i.e. their Z-axis should point downward. However, we are less interested in restricting their rotation in the horizontal plane. You can use this `rot_mask` flexibly to achieve your desired goal pose. Similarly, there's `pos_mask` you can use for masking out position along x/y/z axes.
- We used `scene.draw_debug_frame()` to create visual markers for the target poses. These debug objects are managed at the visualizer level and do not participate in the simulation. Instead of clearing and recreating them every frame, we use `scene.update_debug_objects()` to efficiently update their transforms in place.
- Since this example doesn't involve any physics, after we set the position of the robot, we don't need to call physical simulation via `scene.step()`; instead, we can only update the visualizer to reflect the change in the viewer (and camera, if any) by calling `scene.visualizer.update()`.

### IK for parallel simulation

Genesis allows you to solve IK even when you are in batched environments. Let's spawn 16 parallel envs and let each of the robot's end-effector rotation at a different angular speed:

```python
import numpy as np
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit = False,
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_pos    = (0.0, -2, 1.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 200,
    ),
    show_viewer=True,
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## build ##########################
n_envs = 16
scene.build(n_envs=n_envs, env_spacing=(1.0, 1.0))

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1]) # pointing downwards
center = np.tile(np.array([0.4, -0.2, 0.25]), [n_envs, 1])
angular_speed = np.random.uniform(-10, 10, n_envs)
r = 0.1

ee_link = robot.get_link('hand')

for i in range(0, 1000):
    target_pos = np.zeros([n_envs, 3])
    target_pos[:, 0] = center[:, 0] + np.cos(i/360*np.pi*angular_speed) * r
    target_pos[:, 1] = center[:, 1] + np.sin(i/360*np.pi*angular_speed) * r
    target_pos[:, 2] = center[:, 2]
    target_q = np.hstack([target_pos, target_quat])

    q = robot.inverse_kinematics(
        link     = ee_link,
        pos      = target_pos,
        quat     = target_quat,
        rot_mask = [False, False, True], # for demo purpose: only restrict direction of z-axis
    )

    robot.set_qpos(q)
    scene.step()
```
When dealing with parallel envs, all you have to do is make sure you insert an extra batch dimension into your target pose variables.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/batched_IK.mp4" type="video/mp4">
</video>
