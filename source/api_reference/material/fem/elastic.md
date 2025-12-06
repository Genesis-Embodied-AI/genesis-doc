# `gs.materials.FEM.Elastic`

## 概述
`Elastic` 是 FEM（有限元方法）的弹性材料类，用于模拟具有弹性特性的物体。

## 主要功能
- 支持多种本构模型（线性弹性、稳定 Neo-Hookean、线性共旋转）
- 可配置的杨氏模量、泊松比和密度
- 支持水弹性接触和摩擦
- 提供能量和应力计算功能

## 参数说明

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| E | float | 1e6 | 杨氏模量，控制材料的刚度 |
| nu | float | 0.2 | 泊松比，描述材料在应力下的体积变化 |
| rho | float | 1000 | 材料密度（kg/m³） |
| hydroelastic_modulus | float | 1e7 | 水弹性接触的水弹性模量 |
| friction_mu | float | 0.1 | 摩擦系数 |
| model | str | 'linear' | 应力计算使用的本构模型，可选值：'linear'、'stable_neohookean'、'linear_corotated' |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.FEM.elastic.Elastic
    :members:
    :show-inheritance:
    :undoc-members:
```
