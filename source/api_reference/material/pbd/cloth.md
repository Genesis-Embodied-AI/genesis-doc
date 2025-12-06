# `gs.materials.PBD.Cloth`

## 概述

`Cloth` 是 PBD (Position Based Dynamics) 模拟中使用的布料材料类，用于模拟柔性布料的力学特性。该类基于弹性材料扩展，专门针对布料的拉伸、弯曲和空气阻力等特性进行了优化。

## 主要功能

- 实现了布料的拉伸和弯曲约束
- 支持空气阻力模拟
- 提供摩擦系数配置
- 支持可调节的约束松弛参数
- 适用于模拟各种布料材质（如丝绸、棉布、皮革等）

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `rho` | float | 1000 | 密度 (kg/m³)，布料单位体积的质量 |
| `static_friction` | float | 0.15 | 静摩擦系数，控制布料与其他物体开始滑动前的最大切向力 |
| `kinetic_friction` | float | 0.0 | 动摩擦系数，控制布料与其他物体滑动过程中的阻力 |
| `stretch_compliance` | float | 0.0 | 拉伸柔度 (m/N)，控制布料拉伸约束的柔软度 |
| `bending_compliance` | float | 0.0 | 弯曲柔度 (rad/N)，控制布料的弯曲难易程度 |
| `stretch_relaxation` | float | 0.3 | 拉伸松弛参数，较小的值会减弱拉伸约束 |
| `bending_relaxation` | float | 0.1 | 弯曲松弛参数，较小的值会减弱弯曲约束 |
| `air_resistance` | float | 1e-3 | 空气阻力系数，控制布料在空气中运动时受到的阻力 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.PBD.cloth.Cloth
    :members:
    :show-inheritance:
    :undoc-members:
```
