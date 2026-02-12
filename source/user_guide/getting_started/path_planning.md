# 🗺️ 路径规划

Genesis 提供基于 RRT 的运动规划，用于无碰撞机器人路径。

## 基本用法

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
obstacle = scene.add_entity(gs.morphs.Box(pos=(0.5, 0, 0.3), size=(0.1, 0.3, 0.3), fixed=True))
scene.build()

# 定义目标配置
goal_qpos = robot.inverse_kinematics(
    link=robot.get_link("hand"),
    pos=np.array([0.6, 0.0, 0.3]),
)

# 规划无碰撞路径
path = robot.plan_path(qpos_goal=goal_qpos, num_waypoints=200)

# 执行路径
for waypoint in path:
    robot.control_dofs_position(waypoint)
    scene.step()
```

## 参数

```python
robot.plan_path(
    qpos_goal,                  # 目标配置 (必需)
    qpos_start=None,            # 起始配置 (默认: 当前)
    planner="RRTConnect",       # "RRT" 或 "RRTConnect"
    num_waypoints=300,          # 输出路径长度
    resolution=0.05,            # 规划分辨率
    smooth_path=True,           # 应用路径平滑
    max_nodes=4000,             # 最大树大小
    timeout=None,               # 每次尝试的超时时间 (秒)
    max_retry=1,                # 重试次数
    ignore_collision=False,     # 跳过碰撞检查
)
```

## 规划器类型

- **RRTConnect** (默认): 双向，更高效
- **RRT**: 单树，更简单

## 携带物体的规划

携带物体时进行规划：

```python
path = robot.plan_path(
    qpos_goal=target_qpos,
    ee_link_name="hand",
    with_entity=cube,
)
```

## 检查规划成功

```python
path, is_valid = robot.plan_path(
    qpos_goal=target_qpos,
    return_valid_mask=True,
)

if is_valid:
    print("规划成功！")
```

## 多环境规划

```python
scene.build(n_envs=16)

# 为所有环境规划
path = robot.plan_path(qpos_goal=target_qpos)
print(path.shape)  # (num_waypoints, 16, n_dofs)

# 为特定环境规划
path, valid = robot.plan_path(
    qpos_goal=target_qpos,
    envs_idx=[0, 5, 10],
    return_valid_mask=True,
)
```

## 性能提示

- 增加 `resolution` 以获得更快（质量较低）的规划
- 减少 `resolution` 以获得更平滑的路径
- 使用 `timeout` 和 `max_retry` 以提高可靠性
- `RRTConnect` 通常比 `RRT` 更快
