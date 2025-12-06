# `gs.materials.MPM.Snow`

## 概述

`Snow` 是 MPM (Material Point Method) 模拟中使用的雪材料类，是一种特殊的弹塑性材料，当被压缩时会变硬。该类实现了专门的雪力学模型，可以模拟雪的堆积、压实、坍塌等行为。

## 主要功能

- 实现了雪的特殊力学模型（受压变硬特性）
- 模拟雪的堆积、压实、坍塌等行为
- 不支持 von Mises 屈服准则
- 提供灵活的材料参数配置
- 支持多种粒子采样方法

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量，衡量雪的刚度，默认值为 1e6 |
| `nu` | float | 0.2 | 泊松比，描述雪在受力时的横向收缩特性，默认值为 0.2 |
| `rho` | float | 1000 | 密度 (kg/m³)，雪单位体积的质量，默认值为 1000 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数（剪切模量），默认通过 E 和 nu 计算 |
| `sampler` | str | 'random' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `yield_lower` | float | 2.5e-2 | 屈服条件的下限，默认值为 2.5e-2 |
| `yield_higher` | float | 4.5e-3 | 屈服条件的上限，默认值为 4.5e-3 |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.snow.Snow
    :members:
    :show-inheritance:
    :undoc-members:
```
