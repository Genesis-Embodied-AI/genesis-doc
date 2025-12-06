# `Emitter`

`Emitter` 是 Genesis 引擎中用于发射粒子的实体类，可以创建和发射各种类型的粒子，用于模拟烟雾、火焰、流体等效果。

## 功能说明

- 支持各种类型粒子的发射，如流体粒子、烟雾粒子等
- 可配置发射速率、方向、范围等参数
- 支持动态调整发射属性
- 可以与其他实体进行交互

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
| `emission_rate` | float | 粒子发射速率 |
| `emission_direction` | list | 粒子发射方向 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.emitter.Emitter
    :members:
    :show-inheritance:
    :undoc-members:
```
