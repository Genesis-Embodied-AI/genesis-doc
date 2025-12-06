# `PBDParticleEntity`

`PBDParticleEntity` 是 PBD 系统中的基本粒子实体，用于模拟离散粒子系统。它包含一组粒子及其相关的物理属性和约束。

## 功能说明

该类提供了创建和管理粒子系统的基本功能，支持设置粒子的位置、速度、质量等属性，并可以应用各种物理约束。

## 主要属性

| 属性名称 | 描述 |
|---------|------|
| `idx` | 实体在场景中的唯一索引 |
| `uid` | 实体的唯一标识符 |
| `scene` | 实体所属的场景对象 |
| `sim` | 模拟器对象 |
| `solver` | PBD 求解器对象 |
| `material` | 实体的材料属性 |
| `morph` | 实体的形态参数 |
| `surface` | 实体的表面属性 |
| `mesh` | 实体的网格数据 |
| `vmesh` | 实体的可视化网格 |
| `is_built` | 实体是否已构建完成 |
| `particle_start` | 实体粒子在全局粒子缓冲区中的起始索引 |
| `particle_end` | 实体粒子在全局粒子缓冲区中的结束索引 |
| `n_particles` | 实体包含的粒子数量 |
| `particle_size` | 粒子的大小 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.pbd_entity.PBDParticleEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
