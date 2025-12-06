# `gs.options.SFOptions`

## 概述

`SFOptions` 是 Genesis 中配置 SF（Smoke/Fire，烟雾/火焰）求解器的选项类，用于设置烟雾/火焰模拟的参数，如时间步长、分辨率、求解器迭代次数、衰减系数、温度阈值以及入口参数等。

## 主要功能

- 配置 SF 求解器的时间步长
- 设置模拟分辨率
- 调整求解器迭代次数
- 配置温度阈值和衰减系数
- 设置入口参数（位置、速度、方向、强度）

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `res` | Optional[int] | 128 | 模拟分辨率。 |
| `solver_iters` | Optional[int] | 500 | 求解器迭代次数。 |
| `decay` | Optional[float] | 0.99 | 衰减系数。 |
| `T_low` | Optional[float] | 1.0 | 低温阈值。 |
| `T_high` | Optional[float] | 0.0 | 高温阈值。 |
| `inlet_pos` | Optional[tuple[int, int, int]] | (0.6, 0.0, 0.1) | 入口位置。 |
| `inlet_vel` | Optional[tuple[int, int, int]] | (0, 0, 1) | 入口速度。 |
| `inlet_quat` | Optional[tuple[int, int, int, int]] | (1, 0, 0, 0) | 入口方向（四元数）。 |
| `inlet_s` | Optional[float] | 400.0 | 入口强度。 |


```{eval-rst}  
.. autoclass:: genesis.options.solvers.SFOptions
```
