# `MPMEntity`

`MPMEntity` 是 Genesis 引擎中基于物质点法 (MPM) 的实体类，用于模拟各种复杂的可变形物体和流体，如沙子、水、塑料等。

## 功能说明

- 基于物质点法模拟连续介质的物理行为
- 支持各种材料模型，如弹性体、塑性体、流体等
- 提供粒子位置、速度、密度等状态的获取和设置接口
- 支持大变形和复杂的物理交互

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
| `n_particles` | int | 物质点的数量 |
| `particle_size` | float | 每个物质点的大小 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.mpm_entity.MPMEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
