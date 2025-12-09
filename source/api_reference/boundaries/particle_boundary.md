# ParticleBoundary

`ParticleBoundary` 是 Genesis 引擎中用于定义粒子系统边界的类，用于限制粒子的运动范围并处理粒子与边界的交互。

## 功能说明

`ParticleBoundary` 类提供了以下核心功能：

- 粒子系统的边界定义
- 粒子与边界的碰撞检测和响应
- 边界的几何形状配置
- 粒子边界条件设置

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 边界在系统中的唯一索引 |
| `uid` | `int` | 边界的全局唯一标识符 |
| `name` | `str` | 边界的名称 |
| `type` | `str` | 边界类型，固定为 "particle" |
| `position` | `vector` | 边界位置 |
| `rotation` | `quaternion` | 边界旋转 |
| `scale` | `vector` | 边界缩放 |
| `geometry_type` | `str` | 几何类型（如 "box", "sphere", "cylinder" 等） |
| `boundary_condition` | `str` | 边界条件（如 "reflective", "absorbing", "periodic" 等） |
| `is_built` | `bool` | 边界是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建粒子边界，初始化几何和边界条件 |
| `update()` | 无 | `None` | 更新边界状态 |
| `reset()` | 无 | `None` | 重置边界到初始状态 |
| `set_boundary_condition()` | `str` | `None` | 设置边界条件类型 |
| `check_particle_collision()` | `array` | `array` | 检查粒子与边界的碰撞 |
| `resolve_particle_collision()` | `array, array` | `None` | 处理粒子与边界的碰撞响应 |

## 继承关系

```
BaseBoundary
└── ParticleBoundary
```

```{eval-rst}
.. autoclass:: genesis.engine.boundaries.particle_boundary.ParticleBoundary
    :members:
    :show-inheritance:
    :undoc-members:
```
