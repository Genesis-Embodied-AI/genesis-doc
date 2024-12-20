# 🧗 高级和并行逆运动学 (IK)

Genesis中的IK求解器具有许多强大的功能。在本示例中，我们将展示如何配置IK求解器以接受更灵活的目标姿态，以及如何在批处理设置中为机器人求解。

### 具有多个末端执行器链接的IK

在这个示例中，我们将使用机器人夹爪的左右手指作为两个独立的目标链接。此外，我们不会使用完整的6自由度姿态作为每个链接的目标姿态，而是仅考虑它们的位置和z轴的方向。

```python
import numpy as np

import genesis as gs

########################## 初始化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

########################## 创建场景 ##########################
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

########################## 实体 ##########################

scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

# 两个用于可视化的目标链接
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

########################## 构建 ##########################
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
        rot_mask = [False, False, True], # 仅限制z轴方向
    )

    # 注意，这个IK仅用于可视化目的，因此这里我们不调用scene.step()，而仅更新状态和可视化器
    # 在实际控制应用中，您应该使用robot.control_dofs_position()和scene.step()
    robot.set_dofs_position(q)
    scene.visualizer.update()
```

您将看到以下内容：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/ik_multilink.mp4" type="video/mp4">
</video>

在这个示例中，我们希望您能学到以下几点新知识：

- 我们使用了`robot.inverse_kinematics_multilink()` API来解决考虑多个目标链接的IK问题。使用此API时，我们传入目标链接对象列表、目标位置列表和目标方向（四元数）列表。
- 我们使用`rot_mask`来屏蔽我们不关心的轴方向。在这个示例中，我们希望两个手指都指向下方，即它们的Z轴应该指向下方。然而，我们对它们在水平面内的旋转限制不太感兴趣。您可以灵活使用此`rot_mask`来实现所需的目标姿态。同样地，还有`pos_mask`可以用于屏蔽x/y/z轴上的位置。
- 由于此示例不涉及任何物理学，在设置了机器人和两个目标链接的位置后，我们不需要通过`scene.step()`调用物理仿真；相反，我们只需调用`scene.visualizer.update()`来更新可视化器，以反映查看器（和相机，如果有的话）中的变化。
- **什么是qpos？** 请注意，我们使用`set_qpos`来设置目标链接的状态。`qpos`表示实体在广义坐标中的配置。对于单臂，其`qpos`与其`dofs_position`相同，并且其所有关节（旋转+平移）只有1个自由度。对于通过自由关节连接到`world`的自由网格，该关节有6个自由度（3个平移+3个旋转），而其广义坐标`q`是一个7向量，本质上是其xyz平移+wxyz四元数，因此其`qpos`不同于其`dofs_position`。您可以使用`set_qpos()`和`set_dofs_position()`来设置其状态，但由于这里我们知道所需的四元数，因此更容易计算`qpos`。简而言之，这种差异来自我们如何表示旋转，可以表示为3向量（绕3个轴的旋转）或4向量（wxyz四元数）。

### 并行仿真的IK

Genesis允许您在批处理环境中解决IK问题。让我们生成16个并行环境，并让每个机器人的末端执行器以不同的角速度旋转：

```python
import numpy as np
import genesis as gs

########################## 初始化 ##########################
gs.init()

########################## 创建场景 ##########################
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

########################## 实体 ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## 构建 ##########################
n_envs = 16
scene.build(n_envs=n_envs, env_spacing=(1.0, 1.0))

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1]) # 指向下方
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
        rot_mask = [False, False, True], # 演示目的：仅限制z轴方向
    )

    robot.set_qpos(q)
    scene.step()
```

在处理并行环境时，您只需确保在目标姿态变量中插入一个额外的批处理维度。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/batched_IK.mp4" type="video/mp4">
</video>

