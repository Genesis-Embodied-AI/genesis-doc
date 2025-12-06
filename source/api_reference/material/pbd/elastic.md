# `gs.materials.PBD.Elastic`

## 概述

`Elastic` 是 PBD (Position Based Dynamics) 模拟中使用的弹性材料类，用于模拟具有弹性变形特性的物体。该类实现了基于位置的约束求解器，可以模拟弹性体的拉伸、弯曲和体积保持等行为。

## 主要功能

- 实现了基于位置的弹性约束求解
- 支持拉伸、弯曲和体积约束
- 提供摩擦系数配置
- 支持可调节的约束松弛参数
- 适用于模拟各种弹性体材料

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `rho` | float | 1000 | 密度 (kg/m³)，材料单位体积的质量 |
| `static_friction` | float | 0.15 | 静摩擦系数，控制粒子间开始滑动前的最大切向力 |
| `kinetic_friction` | float | 0.0 | 动摩擦系数，控制粒子滑动过程中的阻力 |
| `stretch_compliance` | float | 0.0 | 拉伸柔度 (m/N)，控制粒子间拉伸约束的柔软度 |
| `bending_compliance` | float | 0.0 | 弯曲柔度 (rad/N)，控制材料的弯曲难易程度 |
| `volume_compliance` | float | 0.0 | 体积柔度 (m³/N)，控制四面体单元的可压缩性 |
| `stretch_relaxation` | float | 0.1 | 拉伸松弛参数，较小的值会减弱拉伸约束 |
| `bending_relaxation` | float | 0.1 | 弯曲松弛参数，较小的值会减弱弯曲约束 |
| `volume_relaxation` | float | 0.1 | 体积松弛参数，较小的值会减弱体积约束 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.PBD.elastic.Elastic
    :members:
    :show-inheritance:
    :undoc-members:
```
