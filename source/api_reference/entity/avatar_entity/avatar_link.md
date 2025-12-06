# `AvatarLink`

`AvatarLink` 是 Avatar 实体中的链接组件，类似于 RigidLink，但使用 `AvatarGeom` 和 `AvatarVisGeom` 来处理碰撞和可视化。

## 功能描述

`AvatarLink` 代表 Avatar 实体中的一个刚性链接，是构成 Avatar 骨架结构的基本单元。每个链接可以包含多个几何形状（用于碰撞检测）和可视化几何形状（用于渲染），并具有质量、惯性等物理属性。链接之间通过关节（Joint）连接，形成完整的骨架结构。

## 主要属性

- `name`: 链接名称
- `pos`, `quat`: 链接位置和四元数
- `inertial_mass`: 链接质量
- `inertial_pos`, `inertial_quat`: 惯性系位置和四元数
- `inertial_i`: 惯性张量
- `geoms`: 碰撞几何形状列表
- `vgeoms`: 可视化几何形状列表
- `joints`: 链接所属的关节列表
- `parent_idx`, `child_idxs`: 父链接索引和子链接索引列表
- `is_fixed`: 链接是否固定
- `is_leaf`: 链接是否为叶节点

## 主要方法

- `get_pos()`: 获取链接位置
- `get_quat()`: 获取链接四元数
- `get_ang()`: 获取链接角速度
- `get_vel()`: 获取链接线速度
- `get_mass()`: 获取链接质量
- `get_AABB()`: 获取链接的轴对齐包围盒
- `get_verts()`: 获取碰撞几何形状的顶点
- `get_vverts()`: 获取可视化几何形状的顶点
- `set_friction(value)`: 设置摩擦系数
- `set_mass(value)`: 设置链接质量


```{eval-rst}  
.. autoclass:: genesis.engine.entities.avatar_entity.avatar_link.AvatarLink
    :members:
    :show-inheritance:
    :undoc-members:
```
