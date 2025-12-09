# SolverState

`SolverState` 是 Genesis 引擎中用于存储求解器内部状态信息的类，包含了求解器的计算数据、迭代状态等信息。每个求解器都有一个对应的 `SolverState` 对象来管理其内部状态。

## 功能说明

`SolverState` 类提供了以下核心功能：

- 求解器内部计算数据的存储
- 迭代状态和收敛信息的管理
- 求解器参数的动态存储
- 求解器状态的复制和重置
- 状态的序列化和反序列化

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 状态在系统中的唯一索引 |
| `uid` | `int` | 状态的全局唯一标识符 |
| `solver_idx` | `int` | 对应的求解器索引 |
| `iterations` | `int` | 当前迭代次数 |
| `residual` | `float` | 求解残差 |
| `converged` | `bool` | 求解是否收敛 |
| `time_step` | `float` | 当前时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `internal_data` | `dict` | 求解器内部数据 |
| `is_initialized` | `bool` | 状态是否已初始化 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `initialize()` | 无 | `None` | 初始化求解器状态 |
| `update()` | 无 | `None` | 更新求解器状态 |
| `reset()` | 无 | `None` | 重置求解器状态到初始值 |
| `copy()` | 无 | `SolverState` | 创建求解器状态的副本 |
| `serialize()` | 无 | `dict` | 将求解器状态序列化为字典 |
| `deserialize()` | `dict` | `None` | 从字典反序列化求解器状态 |
| `set_converged()` | `bool` | `None` | 设置求解收敛状态 |
| `set_residual()` | `float` | `None` | 设置求解残差 |

## 继承关系

```
BaseState
└── SolverState
```

```{eval-rst}
.. autoclass:: genesis.engine.states.solver_state.SolverState
    :members:
    :show-inheritance:
    :undoc-members:
```
