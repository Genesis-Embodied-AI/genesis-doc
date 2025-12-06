# `gs.materials.MPM.Elastic`

## 概述

`Elastic` 是 MPM (Material Point Method) 模拟中使用的弹性材料类，用于模拟具有线性弹性特性的物体。该类实现了多种应力模型，并支持不同的粒子采样方法。

## 主要功能

- 实现了线性弹性本构模型
- 支持多种应力模型（corotation 和 neohooken）
- 提供灵活的材料参数配置
- 支持多种粒子采样方法（pbs、regular、random）
- 基于 Lame 参数计算弹性特性

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量，衡量材料的刚度 |
| `nu` | float | 0.2 | 泊松比，描述材料在受力时的横向收缩特性 |
| `rho` | float | 1000 | 密度 (kg/m³)，材料单位体积的质量 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数（剪切模量），默认通过 E 和 nu 计算 |
| `sampler` | str | 'pbs' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `model` | str | 'corotation' | 应力模型，可选值：'corotation'、'neohooken' |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.elastic.Elastic
    :members:
    :show-inheritance:
    :undoc-members:
```
