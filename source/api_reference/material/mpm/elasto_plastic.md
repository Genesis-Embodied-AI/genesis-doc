# `gs.materials.MPM.ElastoPlastic`

## 概述

`ElastoPlastic` 是 MPM (Material Point Method) 模拟中使用的弹塑性材料类，用于模拟同时具有弹性和塑性变形特性的物体。该类支持多种屈服准则，可以模拟材料在超过弹性极限后的塑性流动行为。

## 主要功能

- 结合了弹性和塑性变形特性
- 支持多种屈服准则（von Mises、Drucker-Prager 等）
- 提供灵活的材料参数配置
- 支持多种粒子采样方法
- 基于 Lame 参数计算弹性特性

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量，衡量材料的刚度 |
| `nu` | float | 0.2 | 泊松比，描述材料在受力时的横向收缩特性 |
| `rho` | float | 1000 | 密度 (kg/m³)，材料单位体积的质量 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数（剪切模量），默认通过 E 和 nu 计算 |
| `sampler` | str | 'random' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `yield_criterion` | str | 'von_mises' | 屈服准则，可选值：'von_mises'、'drucker_prager' 等 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.elasto_plastic.ElastoPlastic
    :members:
    :show-inheritance:
    :undoc-members:
```
