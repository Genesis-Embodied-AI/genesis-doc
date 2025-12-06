# `Scene`

`Scene` 是 Genesis 引擎中用于管理模拟场景的核心类，它包含了模拟器、实体、传感器等所有模拟组件，是物理模拟的容器。

## 功能说明

- 管理场景中的所有实体和组件
- 提供实体的添加、删除和查询接口
- 控制模拟的运行、暂停和重置
- 支持场景状态的保存和加载

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `simulator` | Simulator | 场景中的模拟器对象 |
| `entities` | list | 场景中的所有实体列表 |
| `n_entities` | int | 场景中的实体数量 |
| `time` | float | 当前模拟时间 |
| `step` | int | 当前模拟步数 |

```{eval-rst}  
.. autoclass:: genesis.engine.scene.Scene
    :members:
    :undoc-members:
```