# `gs.options.SimOptions`

## 概述

`SimOptions` 是 Genesis 中配置顶层模拟器的选项类，它指定了模拟器的全局设置，如时间步长、重力、子步数等。这些设置将应用于所有求解器，除非求解器自身的选项中指定了不同的值。

## 主要功能

- 配置模拟器的全局时间步长和子步数
- 设置重力和地板高度
- 启用或禁用可微分模式
- 配置接触处理方式
- 为所有求解器提供默认设置

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | float | 0.01 | 每个模拟步骤的时间持续时间（秒） |
| `substeps` | int | 1 | 每个模拟步骤的子步骤数量 |
| `substeps_local` | Optional[int] | None | 存储在GPU内存中的子步骤数量，用于可微分模式 |
| `gravity` | tuple | (0.0, 0.0, -9.81) | 重力加速度（N/kg），默认指向负z轴方向 |
| `floor_height` | float | 0.0 | 地板的高度（米） |
| `requires_grad` | bool | False | 是否启用可微分模式 |
| `use_hydroelastic_contact` | bool | False | 是否使用水弹性接触 |


```{eval-rst}  
.. autoclass:: genesis.options.solvers.SimOptions
```
