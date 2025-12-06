# `gs.options.PBDOptions`

## 概述

`PBDOptions` 是 Genesis 中配置位置基动力学（PBD）求解器的选项类，用于设置 PBD 模拟的参数，如时间步长、重力、各种约束求解器的迭代次数、粒子大小、空间哈希网格参数和模拟域边界等。

## 主要功能

- 配置 PBD 求解器的时间步长和重力
- 设置各种约束求解器的最大迭代次数（拉伸、弯曲、体积、密度、粘度）
- 定义粒子大小
- 配置空间哈希网格参数
- 设置模拟域的上下边界

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `gravity` | Optional[tuple] | None | 重力加速度（N/kg）。如果为 None，则从 `SimOptions` 继承。 |
| `max_stretch_solver_iterations` | int | 4 | 拉伸约束求解器的最大迭代次数。 |
| `max_bending_solver_iterations` | int | 1 | 弯曲约束求解器的最大迭代次数。 |
| `max_volume_solver_iterations` | int | 1 | 体积约束求解器的最大迭代次数。 |
| `max_density_solver_iterations` | int | 1 | 密度约束求解器的最大迭代次数。 |
| `max_viscosity_solver_iterations` | int | 1 | 粘度约束求解器的最大迭代次数。 |
| `particle_size` | Optional[float] | 0.01 | 粒子直径（米）。 |
| `hash_grid_res` | Optional[tuple] | None | 空间哈希网格的大小（米）。如果为 None，则自动计算。 |
| `hash_grid_cell_size` | Optional[float] | None | 空间哈希网格的单元格大小（米）。这应该至少是 `particle_size` 的 1.25 倍。如果为 None，则自动计算。 |
| `lower_bound` | tuple | (-100.0, -100.0, 0.0) | 模拟域的下界（米）。 |
| `upper_bound` | tuple | (100.0, 100.0, 100.0) | 模拟域的上界（米）。 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.PBDOptions
```
