# `gs.materials.PBD.Liquid`

## 概述

`Liquid` 是 PBD (Position Based Dynamics) 模拟中使用的液体材料类，用于模拟不可压缩流体的力学特性。该类基于粒子的方法实现了流体动力学方程，可以模拟液体的流动、飞溅、表面张力等行为。

## 主要功能

- 实现了不可压缩流体模拟
- 支持密度和粘度约束
- 提供多种粒子采样方法
- 支持可调节的约束松弛参数
- 适用于模拟各种液体（如水、油、蜂蜜等）

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `rho` | float | 1000.0 | 流体的静止密度 (kg/m³)，默认值为水的密度 |
| `sampler` | str | 'pbs' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `density_relaxation` | float | 0.2 | 密度约束的松弛因子，控制位置校正的强度以保证不可压缩性 |
| `viscosity_relaxation` | float | 0.01 | 粘度求解器的松弛因子，影响相邻粒子间相对速度的平滑程度 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.PBD.liquid.Liquid
    :members:
    :show-inheritance:
    :undoc-members:
```
