# RigidBoundary

`RigidBoundary` 是 Genesis 引擎中用于定义刚性边界的类，用于模拟不可变形的物理边界，如墙壁、地面、容器等。

## 功能说明

`RigidBoundary` 类提供了以下核心功能：

- 刚性边界的几何定义（如平面、盒子、球体等）
- 边界的物理属性配置
- 与刚体和变形体的碰撞检测和响应
- 边界运动和变换管理

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 边界在系统中的唯一索引 |
| `uid` | `int` | 边界的全局唯一标识符 |
| `name` | `str` | 边界的名称 |
| `type` | `str` | 边界类型，固定为 "rigid" |
| `position` | `vector` | 边界位置 |
| `rotation` | `quaternion` | 边界旋转 |
| `scale` | `vector` | 边界缩放 |
| `geometry_type` | `str` | 几何类型（如 "plane", "box", "sphere" 等） |
| `friction` | `float` | 边界摩擦系数 |
| `restitution` | `float` | 边界弹性恢复系数 |
| `is_built` | `bool` | 边界是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建刚性边界，初始化几何和物理属性 |
| `update()` | 无 | `None` | 更新边界状态 |
| `reset()` | 无 | `None` | 重置边界到初始状态 |
| `set_geometry()` | `str, dict` | `None` | 设置边界几何类型和参数 |
| `move()` | `vector` | `None` | 移动边界到指定位置 |
| `rotate()` | `quaternion` | `None` | 旋转边界到指定姿态 |

## 继承关系

```
BaseBoundary
└── RigidBoundary
```

```{eval-rst}
.. autoclass:: genesis.engine.boundaries.rigid_boundary.RigidBoundary
    :members:
    :show-inheritance:
    :undoc-members:
```
