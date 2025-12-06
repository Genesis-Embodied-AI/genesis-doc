# `AvatarJoint`

`AvatarJoint` 是 Avatar 实体中连接两个链接（Link）的关节组件，类似于 RigidJoint，但仅用于碰撞检查。

## 功能描述

`AvatarJoint` 定义了 Avatar 实体中两个链接之间的连接关系，包括关节类型、自由度、运动范围和物理属性。它主要用于碰撞检测系统，确保关节连接的正确性，并支持运动学计算。

## 主要属性

- `name`: 关节名称
- `type`: 关节类型（如旋转关节、滑动关节等）
- `pos`, `quat`: 关节位置和四元数
- `link`: 关节所属的链接
- `dof_idx`, `dof_idx_local`: 自由度索引（全局和局部）
- `n_dofs`: 关节自由度数量
- `dofs_limit`: 关节运动范围限制
- `dofs_kp`, `dofs_kv`: 关节刚度和阻尼系数
- `dofs_armature`: 关节电枢（转动惯量）
- `dofs_frictionloss`: 关节摩擦损失
- `init_qpos`: 初始关节位置

## 主要方法

- `get_anchor_pos()`: 获取关节锚点位置
- `get_anchor_axis()`: 获取关节轴方向
- `get_pos()`: 获取关节位置
- `get_quat()`: 获取关节四元数
- `set_sol_params(restitution=None, softness=None)`: 设置求解参数


```{eval-rst}  
.. autoclass:: genesis.engine.entities.avatar_entity.avatar_joint.AvatarJoint
    :members:
    :show-inheritance:
    :undoc-members:
```
