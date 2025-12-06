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

## 代码示例

```python
import genesis as gs

# 初始化 Genesis
gs.init()

# 创建场景
scene = gs.Scene()

# 创建粒子实体
particle_entity = scene.create_particle_entity(
    positions=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],  # 三个粒子的初始位置
    masses=[1.0, 1.0, 1.0],                         # 粒子质量
    particle_size=0.1                              # 粒子大小
)

# 获取粒子信息
print(f"粒子数量: {particle_entity.n_particles}")
print(f"粒子起始索引: {particle_entity.particle_start}")
print(f"粒子结束索引: {particle_entity.particle_end}")
```

```{eval-rst}  
.. autoclass:: genesis.engine.entities.pbd_entity.PBDParticleEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
