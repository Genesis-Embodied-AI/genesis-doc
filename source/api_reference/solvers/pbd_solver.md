# PBDSolver

`PBDSolver` 是基于位置的动力学（Position-Based Dynamics）求解器，用于模拟布料、绳索、软物体等变形体。它通过迭代求解位置约束来实现物理效果，具有良好的稳定性和视觉效果。

## 功能说明

`PBDSolver` 类提供了以下核心功能：

- 基于位置的约束求解
- 布料和绳索模拟
- 碰撞检测和响应
- 多种约束类型支持（距离、弯曲、体积等）
- 可调节的物理参数

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `iterations` | `int` | 求解迭代次数 |
| `constraint_iterations` | `int` | 约束求解迭代次数 |
| `damping` | `float` | 阻尼系数 |
| `stiffness` | `float` | 刚度系数 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 PBD 求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 PBD 模拟 |
| `reset()` | 无 | `None` | 重置 PBD 求解器到初始状态 |
| `solve_constraints()` | 无 | `None` | 求解位置约束 |
| `update_velocities()` | 无 | `None` | 更新粒子速度 |

## 继承关系

```
BaseSolver
└── PBDSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.pbd_solver.PBDSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
