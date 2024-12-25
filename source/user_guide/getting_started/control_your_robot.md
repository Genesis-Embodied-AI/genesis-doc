# 🕹️ 控制机器人

本文将通过完整例子展示如何用各种方式控制机器人。

先导入genesis,创建场景并加载Franka机器人：

```python
import numpy as np
import genesis as gs

########################## 初始化 ##########################
gs.init(backend=gs.gpu)

########################## 创建场景 ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        max_FPS       = 60,
    ),
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    show_viewer = True,
)

########################## 实体 ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)

# 加载实体时，可以在morph中指定其姿态。
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (1.0, 1.0, 0.0),
        euler = (0, 0, 0),
    ),
)

########################## 构建 ##########################
scene.build()
```

如果不给机器人任何驱动力,机械臂会因重力下落。Genesis内置了PD控制器,它接收目标关节位置或速度作为输入。你也可以直接设置关节扭矩/力。

`joint`(关节)和`dof`(自由度)是两个相关概念。以Franka机械臂为例,它的手臂有7个旋转关节,夹爪有2个平移关节,每个关节有1个自由度,总共9个自由度。更一般地,像自由关节(6自由度)或球形关节(3自由度)这样的关节有多个自由度。每个自由度可看作一个可独立控制的电机。

控制关节(自由度)时,需要把URDF/MJCF文件中定义的关节名映射到模拟器内部的自由度索引：

```python
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

注意`.dof_idx_local`获取的是相对机器人实体本身的局部索引,也可用`joint.dof_idx`访问场景中的全局索引。

下面设置各自由度的控制增益,决定了在给定目标位置或速度时控制力的大小。这些信息通常从导入的文件中解析,但建议手动调整:

```python
############ 可选：设置控制增益 ############
# 设置位置增益
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# 设置速度增益
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# 设置安全的力范围
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
```

注意这些API通常需要两个值集作为输入：要设置的实际值和相应的自由度索引。大多数与控制相关的API遵循这种约定。

接下来，我们先看看如何手动设置机器人的配置，而不是使用物理上真实的PD控制器。这些API可以在不遵守物理规律的情况下突然改变机器人的状态：

```python
# 硬重置
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()
```

如果你打开了查看器，你会看到机器人每50步改变一次状态。

接下来，让我们尝试使用内置的PD控制器来控制机器人。Genesis的API设计遵循结构化模式。我们使用`set_dofs_position`来硬设置自由度位置。现在我们只需将`set_*`改为`control_*`来使用控制器对应的API。这里我们展示了不同的控制机器人方式：

```python
# PD控制
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
        # 用速度控制第一个自由度，其余的用位置控制
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
    # 这是根据给定控制命令计算的控制力
    # 如果使用力控制，它与给定的控制命令相同
    print('控制力:', franka.get_dofs_control_force(dofs_idx))

    # 这是自由度实际经历的力
    print('内部力:', franka.get_dofs_force(dofs_idx))

    scene.step()
```

让我们深入了解一下：

- 从第0步到第500步，我们使用位置控制来控制所有自由度，并依次将机器人移动到3个目标位置。注意，对于`control_*`API，一旦设置了目标值，它将被内部存储，你不需要在接下来的步骤中重复发送命令，只要你的目标保持不变。
- 在第750步，我们展示了可以对不同的自由度进行混合控制：对于第一个自由度（自由度0），我们发送一个速度命令，而其余的仍然遵循位置控制命令。
- 在第1000步，我们切换到扭矩（力）控制，并向所有自由度发送一个零力命令，机器人将再次因重力而掉落到地面。

在每一步结束时，我们打印两种类型的力：`get_dofs_control_force()`和`get_dofs_force()`。

- `get_dofs_control_force()`返回控制器施加的力。在位置或速度控制的情况下，这是根据目标命令和控制增益计算的。在力（扭矩）控制的情况下，这与输入的控制命令相同。
- `get_dofs_force()`返回每个自由度实际经历的力，这是控制器施加的力和其他内部力（如碰撞力和科里奥利力）的组合。

如果一切顺利，你应该会看到以下内容：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/control_your_robot.mp4" type="video/mp4">
</video>

以下是涵盖上述所有内容的完整代码脚本：

```python
import numpy as np

import genesis as gs

########################## 初始化 ##########################
gs.init(backend=gs.gpu)

########################## 创建场景 ##########################
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

########################## 实体 ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
    ),
)
########################## 构建 ##########################
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

############ 可选：设置控制增益 ############
# 设置位置增益
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# 设置速度增益
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# 设置安全的力范围
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
# 硬重置
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()

# PD控制
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
        # 用速度控制第一个自由度，其余的用位置控制
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
    # 这是根据给定控制命令计算的控制力
    # 如果使用力控制，它与给定的控制命令相同
    print('控制力:', franka.get_dofs_control_force(dofs_idx))

    # 这是自由度实际经历的力
    print('内部力:', franka.get_dofs_force(dofs_idx))

    scene.step()
```
