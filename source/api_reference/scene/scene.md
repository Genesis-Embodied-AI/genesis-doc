# `Scene`

`Scene` 是 Genesis 引擎中用于管理模拟场景的核心类，它包含了模拟器、实体、传感器等所有模拟组件，是物理模拟的容器。基本上，所有的模拟活动都在场景内部进行。

## 功能说明

- 管理场景中的所有实体和组件
- 提供实体的添加、删除和查询接口
- 控制模拟的运行、暂停和重置
- 支持场景状态的保存和加载
- 提供调试可视化功能
- 支持多相机渲染

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `simulator` | Simulator | 场景中的模拟器对象 |
| `entities` | list | 场景中的所有实体列表 |
| `n_entities` | int | 场景中的实体数量 |
| `time` | float | 当前模拟时间 |
| `step` | int | 当前模拟步数 |

## 主要方法

| 方法名 | 描述 |
| ------ | ---- |
| `add_entity(entity)` | 向场景中添加一个实体 |
| `add_force_field(force_field)` | 向场景中添加一个力场 |
| `add_light(light)` | 向场景中添加一个光源 |
| `add_sensor(sensor)` | 向场景中添加一个传感器 |
| `build()` | 构建场景，这是运行模拟前的必要操作 |
| `step()` | 运行一个模拟时间步 |
| `reset()` | 将场景重置到初始状态 |
| `save_checkpoint(path)` | 保存场景状态到文件 |
| `load_checkpoint(path)` | 从文件加载场景状态 |
| `render_all_cameras()` | 使用批渲染器渲染所有相机的场景 |

```{eval-rst}  
.. autoclass:: genesis.engine.scene.Scene
    :members:
    :undoc-members:
```