# 🧗 高级与并行 IK

Genesis 中的 IK 求解器具有许多强大的功能。在本示例中，我们将展示如何配置 IK 求解器以接受更灵活的目标姿态，以及如何在批量设置中求解。

### 多末端执行器连杆的 IK

在这个示例中，我们将使用机器人夹爪的左手指和右手指作为两个独立的目标连杆。此外，我们不为每个连杆使用完整的 6 自由度姿态作为目标姿态，而是只考虑它们的位置和 Z 轴方向来求解。

```python
import numpy as np

import genesis as gs

########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(2.0, -2, 1.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit=False,
        enable_collision=False,
    ),
)

########################## entities ##########################

scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

# 两个用于可视化的目标连杆
target_left = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/axis.obj',
        scale=0.1,
    ),
    surface=gs.surfaces.Default(color=(1, 0.5, 0.5, 1)),
)
target_right = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/axis.obj',
        scale=0.1,
    ),
    surface=gs.surfaces.Default(color=(0.5, 1.0, 0.5, 1)),
)

########################## build ##########################
scene.build()

target_quat = np.array([0, 1, 0, 0])
center = np.array([0.4, -0.2, 0.25])
r = 0.1

left_finger = robot.get_link('left_finger')
right_finger = robot.get_link('right_finger')

for i in range(0, 2000):
    target_pos_left = center + np.array([np.cos(i/360*np.pi), np.sin(i/360*np.pi), 0]) * r
    target_pos_right = target_pos_left + np.array([0.0, 0.03, 0])

    target_left.set_qpos(np.concatenate([target_pos_left, target_quat]))
    target_right.set_qpos(np.concatenate([target_pos_right, target_quat]))
    
    q = robot.inverse_kinematics_multilink(
        links    = [left_finger, right_finger],
        poss     = [target_pos_left, target_pos_right],
        quats    = [target_quat, target_quat],
        rot_mask = [False, False, True], # 只限制 Z 轴方向
    )

    # 注意，这个 IK 仅用于可视化目的，因此这里我们不调用 scene.step()，只更新状态和可视化器
    # 在实际控制应用中，您应该使用 robot.control_dofs_position() 和 scene.step()
    robot.set_dofs_position(q)
    scene.visualizer.update()
```

这是您将要看到的：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/ik_multilink.mp4" type="video/mp4">
</video>

以下是我们在本示例中希望您了解的一些新内容：
- 我们使用 `robot.inverse_kinematics_multilink()` API 来求解考虑多个目标连杆的 IK。使用此 API 时，我们传入目标连杆对象的列表、目标位置的列表和目标方向（四元数）的列表。
- 我们使用 `rot_mask` 来屏蔽我们不关心的轴方向。在这个示例中，我们希望两个手指都向下指，即它们的 Z 轴应该向下。但是，我们对限制它们在水平平面内的旋转不太感兴趣。您可以灵活地使用这个 `rot_mask` 来实现您想要的目标姿态。同样，您也可以使用 `pos_mask` 来屏蔽沿 x/y/z 轴的位置。
- 由于这个示例不涉及任何物理，在设置机器人和两个目标连杆的位置后，我们不需要通过 `scene.step()` 调用物理仿真；相反，我们只需调用 `scene.visualizer.update()` 来更新查看器（和相机，如果有）中的变化。
- **什么是 qpos？** 注意我们对目标连杆使用了 `set_qpos` 来设置状态。`qpos` 表示实体在广义坐标中的配置。对于单臂，其 `qpos` 与其 `dofs_position` 相同，并且它的所有关节（旋转 + 平移）都只有 1 个自由度。对于一个通过自由关节连接到 `world` 的自由网格，这个关节有 6 个自由度（3 个平移 + 3 个旋转），而其广义坐标 `q` 是一个 7 维向量，本质上是其 xyz 平移 + wxyz 四元数，因此其 `qpos` 与其 `dofs_position` 不同。您可以使用 `set_qpos()` 和 `set_dofs_position()` 来设置其状态，但由于这里我们知道期望的四元数，使用 `qpos` 计算更方便。简而言之，这种差异来自于我们如何表示旋转，旋转可以表示为 3 维向量（绕 3 个轴的旋转）或 4 维向量（wxyz 四元数）。

### 并行仿真的 IK

Genesis 允许您在处于批量环境时求解 IK。让我们生成 16 个并行环境，让每个机器人的末端执行器以不同的角速度旋转：

```python
import numpy as np
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options= gs.options.ViewerOptions(
        camera_pos    = (0.0, -2, 1.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 200,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit = False,
    ),
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

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1]) # 指向下
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
        rot_mask = [False, False, True], # 演示目的：只限制 Z 轴方向
    )

    robot.set_qpos(q)
    scene.step()
```
处理并行环境时，您所要做的就是确保将额外的批处理维度插入到您的目标姿态变量中。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/batched_IK.mp4" type="video/mp4">
</video>
