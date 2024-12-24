# 🧗 高级和并行逆运动学 (IK)

本文将介绍 Genesis 中 IK 求解器的高级功能。我们将展示如何设置灵活的目标姿态，以及如何批量处理机器人的 IK 求解。

## 多末端执行器的 IK 求解

在这个示例中，我们将机器人夹爪的左右手指设为两个独立的目标。我们不会限制手指的完整6自由度姿态，而只关注它们的位置和Z轴方向。

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

# 添加两个可视化的目标标记
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

    # 仅用于可视化，无需物理仿真
    robot.set_dofs_position(q)
    scene.visualizer.update()
```

运行效果如下：

![IK Multilink Demo](https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/ik_multilink.mp4)

代码要点解析：

- `robot.inverse_kinematics_multilink()` 用于求解多目标链接的 IK 问题
- `rot_mask` 可以选择性地限制旋转轴。本例中我们只限制 Z 轴方向，使手指朝下
- 由于不涉及物理仿真，只需调用 `scene.visualizer.update()` 更新显示即可
- `qpos` 和 `dofs_position` 的区别：
  - 对于机械臂，两者相同
  - 对于自由网格，`qpos` 是 7 维向量(xyz位置 + wxyz四元数)
  - `dofs_position` 是 6 维向量(xyz位置 + xyz旋转角)

### 批量处理的 IK 求解

Genesis 支持批量求解 IK 问题。下面我们创建 16 个并行环境，让每个机器人末端执行器以不同速度旋转：

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

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1]) # 使末端朝下
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
        rot_mask = [False, False, True], # 仅限制z轴方向
    )

    robot.set_qpos(q)
    scene.step()
```

在处理并行环境时，只需在目标姿态变量中添加批量维度即可。

![Batched IK Demo](https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/batched_IK.mp4)
