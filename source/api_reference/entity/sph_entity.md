# `SPHEntity`

`SPHEntity` 是 Genesis 引擎中基于光滑粒子流体动力学 (SPH) 的粒子实体类，用于模拟流体效果，如液体、气体等。

## 功能说明

- 基于 SPH 方法模拟流体的运动和相互作用
- 支持各种流体属性，如密度、粘度、表面张力等
- 提供粒子位置、速度、密度等状态的获取和设置接口
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
| `n_particles` | int | 粒子的数量 |
| `particle_size` | float | 每个粒子的大小 |
| `particle_start` | int | 该实体粒子的起始索引 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.sph_entity.SPHEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
