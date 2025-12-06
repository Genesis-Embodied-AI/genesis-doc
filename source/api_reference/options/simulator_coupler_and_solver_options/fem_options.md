# `gs.options.FEMOptions`

## 概述

`FEMOptions` 是 Genesis 中配置有限元方法（FEM）求解器的选项类，用于设置 FEM 模拟的参数，如时间步长、阻尼、重力、求解器类型（显式/隐式）以及各种迭代参数。

## 主要功能

- 配置 FEM 求解器的时间步长和重力
- 设置阻尼参数
- 选择使用显式或隐式求解器
- 配置牛顿迭代参数（用于隐式求解器）
- 设置 PCG 求解器参数（用于隐式求解器）
- 调整线搜索参数（用于隐式求解器）
- 启用/禁用顶点约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `gravity` | Optional[tuple] | None | 重力加速度（N/kg）。如果为 None，则从 `SimOptions` 继承。 |
| `damping` | Optional[float] | 0.0 | 阻尼系数。 |
| `floor_height` | Optional[float] | None | 地板高度（米）。如果为 None，则从 `SimOptions` 继承。 |
| `use_implicit_solver` | bool | False | 是否使用隐式求解器。默认使用显式求解器。 |
| `n_newton_iterations` | int | 1 | 牛顿迭代次数。仅当使用隐式求解器时有效。 |
| `n_pcg_iterations` | int | 500 | PCG 迭代次数。仅当使用隐式求解器时有效。 |
| `n_linesearch_iterations` | int | 0 | 线搜索迭代次数。仅当使用隐式求解器时有效。 |
| `newton_dx_threshold` | float | 1e-06 | 牛顿求解器的阈值。仅当使用隐式求解器时有效。 |
| `pcg_threshold` | float | 1e-06 | PCG 求解器的阈值。仅当使用隐式求解器时有效。 |
| `linesearch_c` | float | 0.0001 | 线搜索充分下降参数。仅当使用隐式求解器时有效。 |
| `linesearch_tau` | float | 0.5 | 线搜索步长缩减因子。仅当使用隐式求解器时有效。 |
| `damping_alpha` | float | 0.5 | 隐式求解器的 Rayleigh 阻尼因子 α。仅当使用隐式求解器时有效。 |
| `damping_beta` | float | 0.0005 | 隐式求解器的 Rayleigh 阻尼因子 β。仅当使用隐式求解器时有效。 |
| `enable_vertex_constraints` | bool | False | 是否启用顶点约束。 |


```{eval-rst}  
.. autoclass:: genesis.options.solvers.FEMOptions
```
