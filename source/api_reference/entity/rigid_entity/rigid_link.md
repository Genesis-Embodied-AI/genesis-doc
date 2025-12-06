# `RigidLink`

`RigidLink` 是 RigidEntity 的基本组成单元，代表一个刚体。每个 RigidEntity 可以包含多个 RigidLink，每个链接可以包含多个碰撞几何形状（RigidGeom）和可视化几何形状（RigidVisGeom）。

## 功能说明

`RigidLink` 类提供了以下主要功能：

- 定义刚体的物理属性（质量、惯性张量）
- 管理碰撞几何形状（RigidGeom）用于碰撞检测
- 管理可视化几何形状（RigidVisGeom）用于渲染
- 处理刚体的位置、姿态和运动
- 提供获取链接边界框、顶点等信息的方法

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 链接在引擎中的全局索引 |
| `idx_local` | `int` | 链接在实体中的局部索引 |
| `uid` | `int` | 链接的唯一标识符 |
| `name` | `str` | 链接的名称 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `geoms` | `list` | 碰撞几何形状列表 |
| `vgeoms` | `list` | 可视化几何形状列表 |
| `joints` | `list` | 关联的关节列表 |
| `n_geoms` | `int` | 碰撞几何形状数量 |
| `n_vgeoms` | `int` | 可视化几何形状数量 |
| `n_joints` | `int` | 关节数量 |
| `n_dofs` | `int` | 自由度数量 |
| `n_qs` | `int` | 状态变量数量 |
| `pos` | `list` | 链接的位置 [x, y, z] |
| `quat` | `list` | 链接的姿态四元数 [w, x, y, z] |
| `inertial_mass` | `float` | 链接的质量 |
| `inertial_pos` | `list` | 惯性中心位置 |
| `inertial_quat` | `list` | 惯性坐标系姿态 |
| `inertial_i` | `list` | 惯性张量 |
| `is_free` | `bool` | 链接是否为自由刚体 |
| `is_leaf` | `bool` | 链接是否为叶节点 |
| `parent_idx` | `int` | 父链接索引 |
| `child_idxs` | `list` | 子链接索引列表 |

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_link.RigidLink
    :members:
    :show-inheritance:
    :undoc-members:
```
