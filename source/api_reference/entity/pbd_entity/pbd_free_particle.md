# `PBDFreeParticleEntity`

`PBDFreeParticleEntity` 是 PBD 系统中的自由粒子实体，用于模拟不受约束的粒子集合。它与 `PBDParticleEntity` 类似，但通常用于模拟不受结构约束的粒子系统，如流体或松散的粒子群。

## 功能说明

该类提供了创建和管理自由粒子系统的功能，支持设置粒子的位置、速度、质量等属性，但不包含结构约束（如连接性约束）。

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

## 代码示例

```python
import genesis as gs
import numpy as np

# 初始化 Genesis
gs.init()

# 创建场景
scene = gs.Scene()

# 生成随机粒子位置
n_particles = 100
positions = np.random.rand(n_particles, 3) * 2 - 1  # 随机分布在 [-1, 1] 立方体中
positions[:, 2] += 2  # 提升到地面以上

# 创建自由粒子实体
free_particle_entity = scene.create_free_particle_entity(
    positions=positions.tolist(),  # 粒子初始位置
    masses=[0.1] * n_particles,    # 每个粒子的质量
    particle_size=0.05             # 粒子大小
)

# 获取粒子信息
print(f"自由粒子数量: {free_particle_entity.n_particles}")
print(f"粒子大小: {free_particle_entity.particle_size}")
```

```{eval-rst}  
.. autoclass:: genesis.engine.entities.pbd_entity.PBDFreeParticleEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
