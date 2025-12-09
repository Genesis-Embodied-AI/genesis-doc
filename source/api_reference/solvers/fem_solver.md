# FEMSolver

`FEMSolver` 是有限元方法（Finite Element Method）求解器，用于高精度弹性体模拟。它通过离散化物体为有限个单元，求解偏微分方程来模拟物体的变形和应力分布。

## 功能说明

`FEMSolver` 类提供了以下核心功能：

- 有限元方法模拟
- 高精度弹性体和肌肉模拟
- 应力和应变计算
- 多种材料模型支持
- 自适应网格细化

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `n_elements` | `int` | 有限元数量 |
| `n_nodes` | `int` | 节点数量 |
| `iterations` | `int` | 求解迭代次数 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 FEM 求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 FEM 模拟 |
| `reset()` | 无 | `None` | 重置 FEM 求解器到初始状态 |
| `compute_stiffness_matrix()` | 无 | `None` | 计算刚度矩阵 |
| `solve_equations()` | 无 | `None` | 求解有限元方程 |

## 继承关系

```
BaseSolver
└── FEMSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.fem_solver.FEMSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
