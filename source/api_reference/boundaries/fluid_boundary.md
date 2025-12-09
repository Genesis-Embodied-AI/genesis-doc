# FluidBoundary

`FluidBoundary` 是 Genesis 引擎中用于定义流体模拟边界的类，用于处理流体与环境的交互和边界条件。

## 功能说明

`FluidBoundary` 类提供了以下核心功能：

- 流体模拟的边界定义
- 流体与边界的交互处理
- 边界条件设置（如无滑移、自由表面等）
- 边界的几何形状配置
- 流体边界的物理属性设置

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 边界在系统中的唯一索引 |
| `uid` | `int` | 边界的全局唯一标识符 |
| `name` | `str` | 边界的名称 |
| `type` | `str` | 边界类型，固定为 "fluid" |
| `position` | `vector` | 边界位置 |
| `rotation` | `quaternion` | 边界旋转 |
| `scale` | `vector` | 边界缩放 |
| `geometry_type` | `str` | 几何类型（如 "box", "cylinder", "custom" 等） |
| `boundary_condition` | `str` | 边界条件（如 "no_slip", "free_slip", "inflow", "outflow" 等） |
| `velocity` | `vector` | 边界速度（用于流入/流出条件） |
| `is_built` | `bool` | 边界是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建流体边界，初始化几何和边界条件 |
| `update()` | 无 | `None` | 更新边界状态 |
| `reset()` | 无 | `None` | 重置边界到初始状态 |
| `set_boundary_condition()` | `str` | `None` | 设置边界条件类型 |
| `set_inflow_velocity()` | `vector` | `None` | 设置流入边界速度 |
| `set_outflow_pressure()` | `float` | `None` | 设置流出边界压力 |

## 继承关系

```
BaseBoundary
└── FluidBoundary
```

```{eval-rst}
.. autoclass:: genesis.engine.boundaries.fluid_boundary.FluidBoundary
    :members:
    :show-inheritance:
    :undoc-members:
```
