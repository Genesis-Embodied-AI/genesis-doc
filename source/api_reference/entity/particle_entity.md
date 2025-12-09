# ParticleEntity

`ParticleEntity` 是 Genesis 引擎中用于粒子系统的实体类，用于创建和管理由离散粒子组成的物理对象。它支持多种粒子模拟类型，如烟雾、火焰、粒子效果等。

## 功能说明

`ParticleEntity` 类提供了以下核心功能：

- 创建和管理大量离散粒子
- 粒子的物理属性和行为控制
- 粒子发射和生命周期管理
- 粒子间的相互作用
- 与其他实体的碰撞检测和响应
- 粒子渲染属性控制

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 实体在场景中的唯一索引 |
| `uid` | `int` | 实体的全局唯一标识符 |
| `name` | `str` | 实体的名称 |
| `n_particles` | `int` | 粒子数量 |
| `particle_positions` | `array` | 粒子位置数组 |
| `particle_velocities` | `array` | 粒子速度数组 |
| `particle_masses` | `array` | 粒子质量数组 |
| `particle_radii` | `array` | 粒子半径数组 |
| `particle_colors` | `array` | 粒子颜色数组 |
| `emission_rate` | `float` | 粒子发射速率 |
| `lifetime` | `float` | 粒子生命周期 |
| `is_built` | `bool` | 实体是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建粒子实体，初始化粒子属性 |
| `update()` | 无 | `None` | 更新粒子状态 |
| `reset()` | 无 | `None` | 重置粒子实体到初始状态 |
| `emit()` | `int` | `None` | 发射指定数量的粒子 |
| `remove_particle()` | `int` | `None` | 移除指定索引的粒子 |
| `clear_particles()` | 无 | `None` | 清除所有粒子 |

## 继承关系

```
BaseEntity
└── ParticleEntity
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.particle_entity.ParticleEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
