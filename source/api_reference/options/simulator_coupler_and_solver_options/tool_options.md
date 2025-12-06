# `gs.options.ToolOptions`

## 概述

`ToolOptions` 是 Genesis 中配置 ToolSolver 的选项类，用于设置工具实体（ToolEntity）的模拟参数。ToolEntity 是 RigidEntity 的简化形式，支持单向工具->其他物体的耦合，但没有内部动力学，只能从单个网格创建。这是可微分刚体-软体交互的临时解决方案，一旦 RigidSolver 支持可微分模式，该求解器将被移除。

## 主要功能

- 配置 ToolSolver 的时间步长
- 设置地板高度

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `floor_height` | Optional[float] | None | 地板的高度（米）。如果为 None，则从 `SimOptions` 继承。 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.ToolOptions
```
