# 🦾 逆运动学与运动规划

本教程演示如何在Genesis中使用逆运动学(IK)和运动规划来完成简单的抓取任务。

先导入需要的包，创建场景并加载机械臂和立方体：

```python
import numpy as np
import genesis as gs

########################## 初始化 ##########################
gs.init(backend=gs.gpu)

########################## 创建场景 ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (3, -1, 1.5),
        camera_lookat = (0.0, 0.0, 0.5), 
        camera_fov    = 30,
        max_FPS       = 60,
    ),
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    show_viewer = True,
)

########################## 创建实体 ##########################
# 添加地面
scene.add_entity(gs.morphs.Plane())

# 添加目标立方体
cube = scene.add_entity(
    gs.morphs.Box(
        size = (0.04, 0.04, 0.04),
        pos  = (0.65, 0.0, 0.02),
    )
)

# 添加Franka机械臂
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## 构建场景 ##########################
scene.build()

# 定义关节索引
motors_dof = np.arange(7)     # 机械臂关节
fingers_dof = np.arange(7, 9) # 夹爪关节

# 设置控制器参数
# 注意：以下值是为实现Franka最佳行为而调整的。
# 有时高质量的URDF或XML文件也会提供这些参数，并会被解析。
franka.set_dofs_kp(
    np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
)
franka.set_dofs_kv(
    np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]), 
)
franka.set_dofs_force_range(
    np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
)
```

```{figure} ../../_static/images/IK_mp_grasp.png
```

然后使用IK和运动规划器移动机械臂到预抓取位置：
Genesis中的运动规划使用OMPL库。你可以按照[安装](../overview/installation.md)页面中的说明进行安装。

```python
# 获取末端执行器链接
end_effector = franka.get_link('hand')

# 用IK求解预抓取位姿的关节角度
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.25]),
    quat = np.array([0, 1, 0, 0]),
)
qpos[-2:] = 0.04  # 夹爪打开

# 规划运动路径
path = franka.plan_path(
    qpos_goal     = qpos,
    num_waypoints = 200, # 2秒时长
)

# 执行规划路径
for waypoint in path:
    franka.control_dofs_position(waypoint)
    scene.step()

# 等待到达最后一个路径点
for i in range(100):
    scene.step()
```

如你所见，IK求解和运动规划都是机器人实体的两个集成方法。对于IK求解，你只需告诉机器人的IK求解器哪个链接是末端执行器，并指定目标姿态。然后，你告诉运动规划器目标关节位置（qpos），它会返回一个规划和平滑的路径点列表。注意，在我们执行路径后，我们让控制器再运行100步。这是因为我们使用的是PD控制器，目标位置和当前实际位置之间会有一个差距。因此，我们让控制器多运行一段时间，以便机器人能够到达规划轨迹的最后一个路径点。

最后执行抓取动作:

```python
# 向下移动到抓取位置
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.135]),
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(100):
    scene.step()

# 夹紧物体
franka.control_dofs_position(qpos[:-2], motors_dof)
franka.control_dofs_force(np.array([-0.5, -0.5]), fingers_dof)
for i in range(100):
    scene.step()

# 抬起物体
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.3]),
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(200):
    scene.step()
```

代码说明：

* IK和运动规划都是机器人实体的内置方法
* IK需要指定目标链接和姿态,返回关节角度
* 运动规划器基于OMPL,设置好目标关节角度后返回平滑路径点
* 执行路径点后需要额外等待一段时间,因为PD控制器需要时间到达目标位置
* 抓取时对夹爪使用力控制,施加0.5N的抓取力
