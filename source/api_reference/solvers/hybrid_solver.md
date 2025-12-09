# HybridSolver

`HybridSolver` 是 Genesis 引擎中用于处理不同物理系统之间相互作用的求解器，它能够将多种求解器组合在一起，实现复杂场景的物理模拟。

## 功能说明

`HybridSolver` 类提供了以下核心功能：

- 多种求解器的集成和协调
- 不同物理系统之间的耦合
- 统一的时间步长管理
- 跨求解器的碰撞检测和响应
- 复杂场景的高效模拟

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `solvers` | `list` | 包含的求解器列表 |
| `n_solvers` | `int` | 求解器数量 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建混合求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的混合模拟 |
| `reset()` | 无 | `None` | 重置混合求解器到初始状态 |
| `add_solver()` | `Solver` | `None` | 添加求解器到混合系统 |
| `remove_solver()` | `int` | `None` | 移除指定索引的求解器 |
| `solve_coupling()` | 无 | `None` | 求解不同求解器之间的耦合 |

## 继承关系

```
BaseSolver
└── HybridSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.hybrid_solver.HybridSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
