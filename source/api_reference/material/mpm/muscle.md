# `gs.materials.MPM.Muscle`

## 概述

`Muscle` 是 MPM (Material Point Method) 模拟中使用的肌肉材料类，用于模拟生物肌肉组织的力学特性。该类支持多个肌肉组，可以模拟肌肉的收缩、伸展等行为，适用于生物力学和角色动画等场景。

## 主要功能

- 模拟生物肌肉组织的力学特性
- 支持多个独立的肌肉组
- 实现肌肉的收缩和伸展行为
- 提供灵活的材料参数配置
- 支持多种应力模型和粒子采样方法

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `E` | float | 1e6 | 杨氏模量，衡量肌肉的刚度，默认值为 1e6 |
| `nu` | float | 0.2 | 泊松比，描述肌肉在受力时的横向收缩特性，默认值为 0.2 |
| `rho` | float | 1000 | 密度 (kg/m³)，肌肉组织单位体积的质量，默认值为 1000 |
| `lam` | float | None | 第一 Lame 参数，默认通过 E 和 nu 计算 |
| `mu` | float | None | 第二 Lame 参数（剪切模量），默认通过 E 和 nu 计算 |
| `sampler` | str | 'pbs' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |
| `model` | str | 'corotation' | 应力模型，可选值：'corotation'、'neohooken' |
| `n_groups` | int | 1 | 肌肉组数量，默认值为 1 |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.MPM.muscle.Muscle
    :members:
    :show-inheritance:
    :undoc-members:
```
