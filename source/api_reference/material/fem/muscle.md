# `gs.materials.FEM.Muscle`

## 概述
`Muscle` 是 FEM（有限元方法）的肌肉材料类，用于模拟具有肌肉特性的物体，支持多肌肉组。

## 主要功能
- 继承自弹性材料，支持多种本构模型
- 支持多个肌肉组，可独立控制
- 可配置的杨氏模量、泊松比和密度
- 提供能量和应力计算功能

## 参数说明

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| E | float | 1e6 | 杨氏模量，控制材料的刚度 |
| nu | float | 0.2 | 泊松比，描述材料在应力下的体积变化 |
| rho | float | 1000 | 材料密度（kg/m³） |
| model | str | 'linear' | 应力计算使用的本构模型，可选值：'linear'、'stable_neohookean' |
| n_groups | int | 1 | 肌肉组的数量 |


```{eval-rst}  
.. autoclass:: genesis.engine.materials.FEM.muscle.Muscle
    :members:
    :show-inheritance:
    :undoc-members:
```
