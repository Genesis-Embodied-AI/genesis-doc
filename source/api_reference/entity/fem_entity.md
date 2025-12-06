# `FEMEntity`

`FEMEntity` 是 Genesis 引擎中基于有限元法 (FEM) 的实体类，用于模拟可变形物体的物理行为，如布料、弹性体等。

## 功能说明

- 基于有限元法模拟物体的变形和应力分布
- 支持各种材料模型，如线性弹性、非线性弹性等
- 提供节点位置、速度、加速度等状态的获取和设置接口
- 支持与其他实体的交互和碰撞

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `idx` | int | 实体在场景中的索引 |
| `uid` | int | 实体的唯一标识符 |
| `is_built` | bool | 实体是否已构建完成 |
| `scene` | Scene | 所属的场景对象 |
| `sim` | Simulator | 所属的模拟器对象 |
| `solver` | Solver | 处理该实体的求解器 |
| `material` | Material | 实体的材料属性 |
| `morph` | Morph | 实体的形态配置 |
| `surface` | Surface | 实体的表面约束或几何 |
| `n_nodes` | int | 有限元网格的节点数量 |
| `n_elements` | int | 有限元网格的单元数量 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.fem_entity.FEMEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
