# `RigidVisGeom`

`RigidVisGeom` 是用于可视化刚体链接的几何形状，与 `RigidGeom` 相对应，但仅用于渲染目的，不参与碰撞检测。每个 RigidLink 可以包含多个 RigidVisGeom，它们共同定义了刚体的可视化外观。

## 功能说明

`RigidVisGeom` 类提供了以下主要功能：

- 定义刚体链接的可视化几何形状
- 设置可视化形状的位置和姿态
- 管理表面材质和纹理
- 提供渲染所需的几何信息
- 支持与碰撞几何形状不同的可视化表示

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 可视化几何形状在引擎中的全局索引 |
| `uid` | `int` | 可视化几何形状的唯一标识符 |
| `link` | `RigidLink` | 所属的刚体链接 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `pos` | `list` | 可视化形状在链接坐标系中的位置 [x, y, z] |
| `quat` | `list` | 可视化形状在链接坐标系中的姿态四元数 [w, x, y, z] |
| `init_pos` | `list` | 初始位置 [x, y, z] |
| `init_quat` | `list` | 初始姿态四元数 [w, x, y, z] |
| `vmesh` | `object` | 可视化网格对象 |
| `n_vverts` | `int` | 可视化顶点数量 |
| `n_vfaces` | `int` | 可视化面数量 |
| `init_vverts` | `list` | 初始可视化顶点坐标 |
| `init_vfaces` | `list` | 初始可视化面索引 |
| `init_vnormals` | `list` | 初始可视化法线向量 |
| `uvs` | `list` | UV 纹理坐标 |
| `surface` | `object` | 表面材质对象 |
| `metadata` | `dict` | 元数据信息 |
| `is_built` | `bool` | 可视化几何形状是否已构建完成 |

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_geom.RigidVisGeom
    :members:
    :show-inheritance:
    :undoc-members:
```
