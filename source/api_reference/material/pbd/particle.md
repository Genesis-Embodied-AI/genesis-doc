# `gs.materials.PBD.Particle`

## 概述

`Particle` 是 PBD (Position Based Dynamics) 模拟中使用的粒子材料类，用于创建没有粒子间相互作用的基于粒子的实体。这些粒子只受外部力（如重力）的影响，适用于创建粒子效果和动画。

## 主要功能

- 创建基于粒子的实体
- 粒子间没有相互作用
- 只受外部力的影响
- 支持多种粒子采样方法
- 适用于创建粒子动画效果

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `rho` | float | 1000.0 | 粒子的密度，默认值为 1000.0 |
| `sampler` | str | 'pbs' | 粒子采样方法，可选值：'pbs'、'regular'、'random' |

```{eval-rst}  
.. autoclass:: genesis.engine.materials.PBD.particle.Particle
    :members:
    :show-inheritance:
    :undoc-members:
```
