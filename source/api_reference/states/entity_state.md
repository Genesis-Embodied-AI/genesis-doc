# EntityState

`EntityState` 是 Genesis 引擎中用于存储实体状态信息的类，包含了实体的位置、速度、姿态等动态属性。每个实体都有一个对应的 `EntityState` 对象来管理其物理状态。

## 功能说明

`EntityState` 类提供了以下核心功能：

- 实体位置、速度、加速度的存储和管理
- 实体姿态（旋转、角速度、角加速度）的管理
- 实体物理属性（质量、惯性等）的存储
- 实体状态的复制和插值
- 状态的序列化和反序列化

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 状态在系统中的唯一索引 |
| `uid` | `int` | 状态的全局唯一标识符 |
| `entity_idx` | `int` | 对应的实体索引 |
| `position` | `vector` | 实体位置 |
| `velocity` | `vector` | 实体速度 |
| `acceleration` | `vector` | 实体加速度 |
| `rotation` | `quaternion` | 实体旋转 |
| `angular_velocity` | `vector` | 实体角速度 |
| `angular_acceleration` | `vector` | 实体角加速度 |
| `scale` | `vector` | 实体缩放 |
| `mass` | `float` | 实体质量 |
| `inertia` | `matrix` | 实体惯性张量 |
| `is_active` | `bool` | 实体是否激活 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `initialize()` | 无 | `None` | 初始化实体状态 |
| `update()` | 无 | `None` | 更新实体状态 |
| `reset()` | 无 | `None` | 重置实体状态到初始值 |
| `copy()` | 无 | `EntityState` | 创建实体状态的副本 |
| `serialize()` | 无 | `dict` | 将实体状态序列化为字典 |
| `deserialize()` | `dict` | `None` | 从字典反序列化实体状态 |
| `interpolate()` | `EntityState, float` | `EntityState` | 在当前状态和目标状态之间插值 |

## 继承关系

```
BaseState
└── EntityState
```

```{eval-rst}
.. autoclass:: genesis.engine.states.entity_state.EntityState
    :members:
    :show-inheritance:
    :undoc-members:
```
