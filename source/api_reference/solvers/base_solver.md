# BaseSolver

`BaseSolver` 是 Genesis 引擎中所有求解器的基类，定义了求解器的核心接口和生命周期管理。它为不同类型的求解器提供了统一的架构和行为模式。

## 功能说明

`BaseSolver` 类提供了以下核心功能：

- 求解器的基本身份标识和配置
- 时间步长管理
- 求解器初始化和构建
- 物理模拟的主要循环（预测、求解、更新）
- 求解器状态管理
- 与实体和场景的交互接口

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `type` | `str` | 求解器类型（如 "rigid", "pbd", "mpm" 等） |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `iterations` | `int` | 求解迭代次数 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建求解器，初始化内部数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的物理模拟 |
| `reset()` | 无 | `None` | 重置求解器到初始状态 |
| `predict()` | 无 | `None` | 预测实体的运动 |
| `solve()` | 无 | `None` | 求解物理约束和力 |
| `update()` | 无 | `None` | 更新实体状态 |

## 继承关系

```
BaseSolver
├── RigidSolver
├── PBDSolver
├── MPMSolver
├── FEMSolver
├── SPHSolver
└── HybridSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.base_solver.BaseSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
