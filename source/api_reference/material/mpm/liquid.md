# `gs.materials.MPM.Liquid`

## 概述

`Liquid` 是 MPM (Material Point Method) 模拟中使用的液体材料类，用于模拟具有不可压缩或可压缩流体特性的物质。该类实现了流体动力学方程，可以模拟液体的流动、飞溅等行为。

## 主要功能

- 实现了流体动力学方程
- 支持不可压缩或可压缩流体模拟
- 提供灵活的流体参数配置
- 支持多种粒子采样方法
- 模拟液体的表面张力和粘性特性

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量（用于可压缩流体），默认值为 1e6 |
| `nu` | float | 0.2 | 泊松比（用于可压缩流体），默认值为 0.2 |
| `rho` | float | 1000 | 密度 (kg/m³)，液体单位体积的质量，默认值为 1000 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数，默认通过 E 和 nu 计算 |
| `sampler` | str | 'random' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `bulk_modulus` | float | None | 体积模量，衡量流体的可压缩性 |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.liquid.Liquid
    :members:
    :show-inheritance:
    :undoc-members:
```
