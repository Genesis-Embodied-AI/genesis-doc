# `gs.options.MPMOptions`

## 概述

`MPMOptions` 是 Genesis 中配置物质点法（MPM）求解器的选项类，用于设置 MPM 模拟的参数，如时间步长、重力、粒子大小、网格密度、模拟域边界等。

## 主要功能

- 配置 MPM 求解器的时间步长和重力
- 设置粒子大小和网格密度
- 启用/禁用 CPIC（兼容粒子单元）以支持与薄物体的耦合
- 定义模拟域的上下边界
- 配置稀疏网格相关参数

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `gravity` | Optional[tuple] | None | 重力加速度（N/kg）。如果为 None，则从 `SimOptions` 继承。 |
| `particle_size` | Optional[float] | None | 粒子直径（米）。如果未指定，将基于 `grid_density` 计算粒子大小。 |
| `grid_density` | float | 64 | 每米的网格单元数量。 |
| `enable_CPIC` | bool | False | 是否启用 CPIC（兼容粒子单元）以支持与薄物体的耦合。 |
| `lower_bound` | tuple | (-1.0, -1.0, 0.0) | 模拟域的下界（米）。 |
| `upper_bound` | tuple | (1.0, 1.0, 1.0) | 模拟域的上界（米）。 |
| `use_sparse_grid` | bool | False | 是否使用稀疏网格。除非了解其影响，否则不建议修改。 |
| `leaf_block_size` | int | 8 | 稀疏模式下叶子块的大小。 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.MPMOptions
```
