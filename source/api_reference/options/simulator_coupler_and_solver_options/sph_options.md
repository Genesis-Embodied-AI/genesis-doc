# `gs.options.SPHOptions`

## 概述

`SPHOptions` 是 Genesis 中配置光滑粒子流体动力学（SPH）求解器的选项类，用于设置 SPH 模拟的参数，如时间步长、重力、粒子大小、压力求解器类型、模拟域边界、哈希网格参数以及各种求解器迭代次数和容差等。

## 主要功能

- 配置 SPH 求解器的时间步长和重力
- 设置粒子大小和压力求解器类型（如 WCSPH、DFSPH）
- 定义模拟域的上下边界
- 配置空间哈希网格参数
- 设置密度和散度求解器的迭代次数和容差

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `gravity` | Optional[tuple] | None | 重力加速度（N/kg）。如果为 None，则从 `SimOptions` 继承。 |
| `particle_size` | float | 0.02 | 粒子直径（米）。 |
| `pressure_solver` | str | "WCSPH" | 压力求解器类型，可选值为 "WCSPH" 或 "DFSPH"。 |
| `lower_bound` | tuple | (-100.0, -100.0, 0.0) | 模拟域的下界（米）。 |
| `upper_bound` | tuple | (100.0, 100.0, 100.0) | 模拟域的上界（米）。 |
| `hash_grid_res` | Optional[tuple] | None | 空间哈希网格的大小（米）。如果为 None，则自动计算。 |
| `hash_grid_cell_size` | Optional[float] | None | 空间哈希网格的单元格大小（米）。这应该至少是 `particle_size` 的 2 倍。如果为 None，则自动计算。 |
| `max_divergence_error` | float | 0.1 | DFSPH 方法的最大散度误差。 |
| `max_density_error_percent` | float | 0.05 | DFSPH 方法的最大密度误差百分比（0.05 表示 0.05%）。 |
| `max_divergence_solver_iterations` | int | 100 | 散度求解器的最大迭代次数。 |
| `max_density_solver_iterations` | int | 100 | 密度求解器的最大迭代次数。 |


```{eval-rst}  
.. autoclass:: genesis.options.solvers.SPHOptions
```
