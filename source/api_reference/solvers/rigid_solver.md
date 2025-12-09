# RigidSolver

`RigidSolver` 是 Genesis 引擎中用于处理刚体动力学的求解器，负责计算刚体的运动、碰撞和约束。它基于经典力学原理，处理刚体之间的相互作用。

## 功能说明

`RigidSolver` 类提供了以下核心功能：

- 刚体动力学计算（位置、速度、加速度）
- 碰撞检测和响应
- 关节约束求解
- 接触力计算
- 刚体链和多体系统处理

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `iterations` | `int` | 求解迭代次数 |
| `tol` | `float` | 求解收敛 tolerance |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建刚体求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的刚体模拟 |
| `reset()` | 无 | `None` | 重置刚体求解器到初始状态 |
| `solve_collisions()` | 无 | `None` | 求解刚体之间的碰撞 |
| `solve_constraints()` | 无 | `None` | 求解关节和约束 |

## 继承关系

```
BaseSolver
└── RigidSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.rigid_solver.RigidSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
