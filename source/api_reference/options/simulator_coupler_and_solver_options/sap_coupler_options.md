# `gs.options.SAPCouplerOptions`

## 概述

`SAPCouplerOptions`是 Genesis 中配置耦合器求解器的选项类，用于设置耦合器的迭代参数、收敛阈值、接触刚度等参数，以控制不同求解器之间的耦合行为。

## 主要功能

- 配置 SAP 耦合器的迭代参数
- 设置 PCG 求解器的收敛阈值
- 调整线搜索迭代参数
- 配置接触刚度参数
- 设置 FEM 和刚体的接触类型
- 启用/禁用刚体与 FEM 之间的耦合

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `n_sap_iterations` | int | 5 | SAP 迭代次数 |
| `n_pcg_iterations` | int | 100 | PCG 迭代次数 |
| `n_linesearch_iterations` | int | 10 | 线搜索迭代次数 |
| `sap_convergence_atol` | float | 1e-06 | SAP 绝对收敛容差 |
| `sap_convergence_rtol` | float | 1e-05 | SAP 相对收敛容差 |
| `sap_taud` | float | 0.1 | SAP 阻尼参数 |
| `sap_beta` | float | 1.0 | SAP 松弛因子 |
| `sap_sigma` | float | 0.001 | SAP 惩罚参数 |
| `pcg_threshold` | float | 1e-06 | PCG 求解器阈值 |
| `linesearch_ftol` | float | 1e-06 | 线搜索函数容差 |
| `linesearch_max_step_size` | float | 1.5 | 线搜索最大步长 |
| `hydroelastic_stiffness` | float | 1e8 | 水弹性接触刚度 |
| `point_contact_stiffness` | float | 1e8 | 点接触刚度 |
| `fem_floor_contact_type` | str | "tet" | FEM 与地板的接触类型，可选值："tet"、"vert"、"none" |
| `enable_fem_self_tet_contact` | bool | True | 是否启用基于四面体的自接触 |
| `rigid_floor_contact_type` | str | "vert" | 刚体与地板的接触类型，可选值："vert"、"none" |
| `enable_rigid_fem_contact` | bool | True | 是否启用刚体与 FEM 求解器之间的耦合 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.SAPCouplerOptions
```
