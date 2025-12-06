# `RigidJoint`

`RigidJoint` 用于定义两个 RigidLink 之间的约束关系，限制它们的相对运动。关节可以有不同的类型，如铰链关节、球关节等，每种类型提供不同的自由度限制。

## 功能说明

`RigidJoint` 类提供了以下主要功能：

- 定义两个刚体链接之间的约束关系
- 支持多种关节类型（铰链、球关节、棱柱、固定等）
- 提供关节的位置和角度控制
- 允许设置关节的物理参数（刚度、阻尼、摩擦等）
- 支持关节的运动限制（角度范围、位移范围等）

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 关节在引擎中的全局索引 |
| `idx_local` | `int` | 关节在实体中的局部索引 |
| `uid` | `int` | 关节的唯一标识符 |
| `name` | `str` | 关节的名称 |
| `type` | `str` | 关节类型（hinge, ball, prismatic, fixed等） |
| `link` | `RigidLink` | 关联的主要链接 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `pos` | `list` | 关节位置 [x, y, z] |
| `quat` | `list` | 关节姿态四元数 [w, x, y, z] |
| `axis` | `list` | 关节轴向量 [x, y, z]（用于铰链和棱柱关节） |
| `n_dofs` | `int` | 关节的自由度数量 |
| `n_qs` | `int` | 关节的状态变量数量 |
| `dofs_idx` | `list` | 关节自由度在全局索引中的位置 |
| `dofs_idx_local` | `list` | 关节自由度在实体中的局部索引 |
| `dofs_kp` | `list` | 位置控制增益 |
| `dofs_kv` | `list` | 速度控制增益 |
| `dofs_stiffness` | `list` | 刚度参数 |
| `dofs_damping` | `list` | 阻尼参数 |
| `dofs_invweight` | `list` | 逆权重 |
| `dofs_frictionloss` | `list` | 摩擦损失 |
| `dofs_limit` | `list` | 运动限制 |
| `dofs_force_range` | `list` | 力范围限制 |
| `dofs_motion_ang` | `list` | 运动角度 |
| `dofs_motion_vel` | `list` | 运动速度 |
| `sol_params` | `list` | 求解器参数 |
| `is_built` | `bool` | 关节是否已构建完成 |

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_joint.RigidJoint
    :members:
    :show-inheritance:
    :undoc-members:
```
