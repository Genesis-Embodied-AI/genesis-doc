# PBDEntity

PBDEntity 是基于位置的动力学（Position-Based Dynamics, PBD）系统中的实体基类，用于模拟柔性物体、流体和其他非刚性体。PBD 是一种高效的物理模拟方法，通过直接约束粒子位置来实现真实的物理行为。

## PBD 实体分类

Genesis 提供了多种 PBD 实体类型，以支持不同的模拟需求：

- **PBDParticleEntity**: 基本的粒子实体，用于模拟离散粒子系统
- **PBDFreeParticleEntity**: 自由粒子实体，不受约束的粒子集合
- **PBD2DEntity**: 2D PBD 实体，用于模拟平面结构（如布料、薄膜）
- **PBD3DEntity**: 3D PBD 实体，用于模拟三维网格结构
- **PBDTetEntity**: 四面体 PBD 实体，用于模拟体积物体（如软组织、弹性体）

```{toctree}
pbd_particle
pbd_free_particle
pbd_2d
pbd_3d
pbd_tet
```
