# BaseState

`BaseState` 是 Genesis 引擎中所有状态类的基类，定义了状态管理的核心接口和功能。它为不同类型的状态提供了统一的架构和行为模式。

## 功能说明

`BaseState` 类提供了以下核心功能：

- 状态的基本身份标识和配置
- 状态数据的存储和访问
- 状态的序列化和反序列化
- 状态的复制和克隆
- 状态的插值和预测
- 状态的重置和初始化

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 状态在系统中的唯一索引 |
| `uid` | `int` | 状态的全局唯一标识符 |
| `name` | `str` | 状态的名称 |
| `type` | `str` | 状态类型（如 "entity", "solver", "scene" 等） |
| `timestamp` | `float` | 状态的时间戳 |
| `is_initialized` | `bool` | 状态是否已初始化 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `initialize()` | 无 | `None` | 初始化状态数据 |
| `update()` | 无 | `None` | 更新状态数据 |
| `reset()` | 无 | `None` | 重置状态到初始状态 |
| `copy()` | 无 | `State` | 创建状态的副本 |
| `serialize()` | 无 | `dict` | 将状态序列化为字典 |
| `deserialize()` | `dict` | `None` | 从字典反序列化状态 |
| `interpolate()` | `State, float` | `State` | 在当前状态和目标状态之间插值 |

## 继承关系

```
BaseState
├── EntityState
├── SolverState
└── SceneState
```

```{eval-rst}
.. autoclass:: genesis.engine.states.base_state.BaseState
    :members:
    :show-inheritance:
    :undoc-members:
```
