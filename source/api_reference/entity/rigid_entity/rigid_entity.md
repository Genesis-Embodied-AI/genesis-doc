# `RigidEntity`

`RigidEntity` 是 Genesis 引擎中刚体系统的核心类，用于创建和管理刚体实体。它可以包含多个刚体链接（RigidLink），通过关节（RigidJoint）连接，形成复杂的机械结构。

## 功能说明

`RigidEntity` 类提供了以下主要功能：

- 创建和管理多个刚体链接（RigidLink）
- 定义链接之间的关节约束（RigidJoint）
- 处理刚体的物理属性（质量、惯性、摩擦等）
- 支持刚体的位置、姿态和运动控制
- 提供碰撞检测和响应机制

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 实体在引擎中的全局索引 |
| `uid` | `int` | 实体的唯一标识符 |
| `name` | `str` | 实体的名称 |
| `links` | `list` | 实体包含的刚体链接列表 |
| `joints` | `list` | 实体包含的关节列表 |
| `n_links` | `int` | 链接数量 |
| `n_joints` | `int` | 关节数量 |
| `n_dofs` | `int` | 自由度数量 |
| `n_qs` | `int` | 状态变量数量 |
| `dofs_idx` | `list` | 自由度在全局索引中的位置 |
| `dofs_stiffness` | `list` | 自由度的刚度参数 |
| `dofs_damping` | `list` | 自由度的阻尼参数 |
| `dofs_kp` | `list` | 位置控制增益 |
| `dofs_kv` | `list` | 速度控制增益 |
| `dofs_invweight` | `list` | 自由度的逆权重 |
| `dofs_frictionloss` | `list` | 自由度的摩擦损失 |
| `dofs_limit` | `list` | 自由度的运动限制 |
| `dofs_force_range` | `list` | 自由度的力范围限制 |
| `is_built` | `bool` | 实体是否已构建完成 |
| `solver` | `object` | 关联的求解器对象 |

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
