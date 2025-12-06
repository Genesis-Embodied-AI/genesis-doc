# `PBD3DEntity`

`PBD3DEntity` 是 PBD 系统中的 3D 实体，用于模拟三维网格结构，如柔性物体、绳索和其他三维柔性结构。它基于四面体或三角形网格构建，支持各种三维物理约束。

## 功能说明

该类提供了创建和管理三维柔性物体的功能，支持设置物体的材料属性、形态参数和物理约束，如拉伸约束、弯曲约束、体积约束和碰撞约束。

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
| `edges` | 实体的边数据 |
| `n_edges` | 实体包含的边数量 |

## 代码示例

```python
import genesis as gs

# 初始化 Genesis
gs.init()

# 创建场景
scene = gs.Scene()

# 创建 3D 柔性物体（例如一个简单的立方体）
cube_entity = scene.create_3d_entity(
    dimensions=[1.0, 1.0, 1.0],  # 立方体尺寸
    segments=[5, 5, 5],           # 每个维度的段数
    pos=[0, 0, 2],                 # 立方体中心位置
    particle_size=0.05,            # 粒子大小
    is_fixed=False                 # 是否固定
)

# 获取实体信息
print(f"立方体粒子数量: {cube_entity.n_particles}")
print(f"立方体元素数量: {cube_entity.n_elems}")
print(f"立方体边数量: {cube_entity.n_edges}")
```

```{eval-rst}  
.. autoclass:: genesis.engine.entities.pbd_entity.PBD3DEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
