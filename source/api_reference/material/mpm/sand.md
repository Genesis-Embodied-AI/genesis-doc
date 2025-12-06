# `gs.materials.MPM.Sand`

## 概述

`Sand` 是 MPM (Material Point Method) 模拟中使用的沙子材料类，用于模拟颗粒状物质的力学特性。该类实现了基于摩擦角的塑性模型，可以模拟沙子的流动、堆积、崩塌等行为。

## 主要功能

- 实现了基于摩擦角的颗粒材料模型
- 模拟沙子的流动、堆积、崩塌等行为
- 支持压力相关的塑性屈服
- 提供灵活的材料参数配置
- 支持多种粒子采样方法

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量，衡量沙子的刚度，默认值为 1e6 |
| `nu` | float | 0.2 | 泊松比，描述沙子在受力时的横向收缩特性，默认值为 0.2 |
| `rho` | float | 1000 | 密度 (kg/m³)，沙子单位体积的质量，默认值为 1000 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数（剪切模量），默认通过 E 和 nu 计算 |
| `sampler` | str | 'random' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `friction_angle` | float | 45 | 摩擦角（度），用于计算内部压力相关的塑性屈服，默认值为 45 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.sand.Sand
    :members:
    :show-inheritance:
    :undoc-members:
```
