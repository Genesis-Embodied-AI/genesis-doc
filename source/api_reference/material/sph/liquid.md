# `gs.materials.SPH.Liquid`

## 概述

`Liquid` 是 SPH (Smoothed Particle Hydrodynamics) 模拟中使用的液体材料类，用于模拟流体的力学特性。SPH 方法通过平滑粒子近似来模拟连续流体，适用于模拟复杂的流体行为，如飞溅、破碎和自由表面流动。

## 主要功能

- 实现了基于SPH方法的流体模拟
- 支持密度、粘度和表面张力参数设置
- 提供多种粒子采样方法
- 支持可调节的状态刚度和指数参数
- 适用于模拟各种液体（如水、油、蜂蜜等）

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `rho` | float | 1000.0 | 流体的静止密度 (kg/m³)，默认值为水的密度 |
| `stiffness` | float | 50000.0 | 状态刚度 (N/m²)，控制压力随压缩的增加程度 |
| `exponent` | float | 7.0 | 状态指数，控制压力随密度的非线性缩放程度 |
| `mu` | float | 0.005 | 流体的粘度，衡量流体内部摩擦的度量 |
| `gamma` | float | 0.01 | 流体的表面张力，控制材料在边界处的"结块"强度 |
| `sampler` | str | 'pbs' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.SPH.liquid.Liquid
    :members:
    :show-inheritance:
    :undoc-members:
```
