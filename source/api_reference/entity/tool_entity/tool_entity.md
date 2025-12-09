# `ToolEntity`

## 概述

`ToolEntity` 是 Genesis 引擎中的工具实体类，是 `RigidEntity` 的简化形式，主要用于支持单向工具到其他物体的耦合交互。它没有内部动力学，只能从单个网格创建，是可微分刚体-软体交互的临时解决方案。

## 主要功能

- 作为 `RigidEntity` 的简化形式，支持基本的刚性体属性
- 实现单向工具到其他物体的耦合交互
- 支持从单个网格创建工具实体
- 用于可微分刚体-软体交互场景
- 由 `ToolOptions` 类配置模拟参数

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 实体在引擎中的全局索引 |
| `uid` | `int` | 实体的唯一标识符 |
| `name` | `str` | 实体的名称 |
| `mesh` | `Mesh` | 工具实体的网格 |
| `position` | `vector` | 实体位置 |
| `rotation` | `quaternion` | 实体旋转 |
| `scale` | `vector` | 实体缩放 |
| `is_built` | `bool` | 实体是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建工具实体，初始化物理属性 |
| `update()` | 无 | `None` | 更新实体状态 |
| `reset()` | 无 | `None` | 重置实体到初始状态 |
| `set_position()` | `vector` | `None` | 设置实体位置 |
| `set_rotation()` | `quaternion` | `None` | 设置实体旋转 |
| `set_scale()` | `vector` | `None` | 设置实体缩放 |

## 使用示例

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 创建工具实体
mesh = gs.Mesh.create_cube()
tool_entity = scene.add_entity(type='tool', mesh=mesh)

# 设置工具实体位置
tool_entity.set_position([0, 0, 1])

# 配置工具求解器选项
scene.options.solver.tool_options.dt = 0.01
scene.options.solver.tool_options.floor_height = 0.0

# 运行模拟
scene.build()
for i in range(100):
    # 在每一帧更新工具实体位置
    tool_entity.set_position([0, 0, 1 + 0.5 * gs.math.sin(i * 0.1)])
    scene.step()

scene.release()
```

## 继承关系

```
BaseEntity
└── ToolEntity
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.tool.ToolEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
