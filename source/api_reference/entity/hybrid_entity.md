# `HybridEntity`

`HybridEntity` 是 Genesis 引擎中用于模拟混合物理系统的实体类，它结合了多种物理模拟方法，如有限元法、粒子法等，用于模拟复杂的物理现象。

## 功能说明

- 结合多种物理模拟方法，提供更灵活的模拟能力
- 支持不同物理模型之间的耦合和转换
- 提供统一的接口来管理混合系统
- 支持与其他实体的交互

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
| `n_components` | int | 混合系统的组件数量 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.hybrid_entity.HybridEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
