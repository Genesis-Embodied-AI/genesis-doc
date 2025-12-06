# `PBD2DEntity`

`PBD2DEntity` 是 PBD 系统中的 2D 实体，用于模拟平面结构，如布料、薄膜和其他二维柔性物体。它基于三角形网格构建，支持各种二维物理约束。

## 功能说明

该类提供了创建和管理二维柔性物体的功能，支持设置物体的材料属性、形态参数和物理约束，如拉伸约束、弯曲约束和碰撞约束。

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
| `elem_start` | 实体元素在全局元素缓冲区中的起始索引 |
| `elem_end` | 实体元素在全局元素缓冲区中的结束索引 |
| `n_elems` | 实体包含的元素数量 |

```{eval-rst}  
.. autoclass:: genesis.engine.entities.pbd_entity.PBD2DEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
