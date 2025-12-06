# `AvatarEntity`

`AvatarEntity` 是 Genesis 中用于表示具有关节和链接结构的复杂实体（如人形机器人、动物等）的核心类。它提供了完整的骨骼动画、物理模拟和控制功能。

## 功能描述

`AvatarEntity` 实现了具有多个链接（Link）和关节（Joint）的骨架结构，支持正向运动学（FK）、逆向运动学（IK）、路径规划和力控制等高级功能。它可以用于模拟人物、动物或其他具有复杂运动结构的实体，并支持与其他物理实体的交互。

## 主要属性

- `links`: 实体的链接列表
- `joints`: 实体的关节列表
- `geoms`: 实体的几何形状列表（用于碰撞检测）
- `vgeoms`: 实体的可视化几何形状列表（用于渲染）
- `n_dofs`: 自由度数量
- `q_start`, `q_end`: 位置状态的起始和结束索引
- `init_qpos`: 初始关节位置
- `material`: 实体材料属性
- `surface`: 表面属性，用于渲染

## 核心功能

### 运动学控制
- `forward_kinematics(qpos=None)`: 执行正向运动学计算
- `inverse_kinematics(target_pos, target_quat=None, link_idx=None)`: 执行逆向运动学计算
- `inverse_kinematics_multilink(targets)`: 执行多链接逆向运动学计算

### 关节控制
- `control_dofs_position(dof_indices, target_positions, kp=None, kv=None)`: 位置控制
- `control_dofs_velocity(dof_indices, target_velocities, kv=None)`: 速度控制
- `control_dofs_force(dof_indices, forces)`: 力控制
- `set_dofs_position(dof_indices, positions)`: 设置关节位置
- `set_dofs_velocity(dof_indices, velocities)`: 设置关节速度

### 状态查询
- `get_dofs_position(dof_indices=None)`: 获取关节位置
- `get_dofs_velocity(dof_indices=None)`: 获取关节速度
- `get_links_pos(link_indices=None)`: 获取链接位置
- `get_links_quat(link_indices=None)`: 获取链接四元数
- `get_links_vel(link_indices=None)`: 获取链接速度

### 碰撞检测
- `detect_collision(other_entity)`: 检测与其他实体的碰撞
- `get_contacts()`: 获取当前碰撞接触点

### 路径规划
- `plan_path(start_qpos, goal_qpos)`: 规划关节空间路径


    scene.step()
```

```{eval-rst}  
.. autoclass:: genesis.engine.entities.avatar_entity.avatar_entity.AvatarEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
