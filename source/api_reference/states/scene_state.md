# SceneState

`SceneState` 是 Genesis 引擎中用于存储整个场景全局状态信息的类，包含了场景的时间、环境参数、全局物理设置等信息。它是场景级别的状态管理器。

## 功能说明

`SceneState` 类提供了以下核心功能：

- 场景时间和帧率管理
- 全局物理参数（重力、阻尼等）的存储
- 环境参数（光照、背景等）的管理
- 场景状态的复制和重置
- 状态的序列化和反序列化

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 状态在系统中的唯一索引 |
| `uid` | `int` | 状态的全局唯一标识符 |
| `time` | `float` | 当前场景时间 |
| `frame` | `int` | 当前场景帧数 |
| `fps` | `float` | 目标帧率 |
| `gravity` | `vector` | 全局重力加速度 |
| `damping` | `float` | 全局阻尼系数 |
| `ambient_light` | `color` | 环境光照颜色 |
| `background_color` | `color` | 背景颜色 |
| `is_paused` | `bool` | 场景是否暂停 |
| `is_initialized` | `bool` | 状态是否已初始化 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `initialize()` | 无 | `None` | 初始化场景状态 |
| `update()` | 无 | `None` | 更新场景状态 |
| `reset()` | 无 | `None` | 重置场景状态到初始值 |
| `copy()` | 无 | `SceneState` | 创建场景状态的副本 |
| `serialize()` | 无 | `dict` | 将场景状态序列化为字典 |
| `deserialize()` | `dict` | `None` | 从字典反序列化场景状态 |
| `set_paused()` | `bool` | `None` | 设置场景暂停状态 |
| `set_time()` | `float` | `None` | 设置场景时间 |

## 继承关系

```
BaseState
└── SceneState
```

```{eval-rst}
.. autoclass:: genesis.engine.states.scene_state.SceneState
    :members:
    :show-inheritance:
    :undoc-members:
```
