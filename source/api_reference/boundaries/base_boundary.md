# BaseBoundary

`BaseBoundary` 是 Genesis 引擎中所有边界的基类，定义了边界的核心接口和生命周期管理。它为不同类型的边界提供了统一的架构和行为模式。

## 功能说明

`BaseBoundary` 类提供了以下核心功能：

- 边界的基本身份标识和配置
- 边界的几何描述和位置管理
- 边界与实体的交互接口
- 边界的生命周期管理
- 与求解器的通信机制

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 边界在系统中的唯一索引 |
| `uid` | `int` | 边界的全局唯一标识符 |
| `name` | `str` | 边界的名称 |
| `type` | `str` | 边界类型（如 "rigid", "particle", "fluid" 等） |
| `position` | `vector` | 边界位置 |
| `rotation` | `quaternion` | 边界旋转 |
| `scale` | `vector` | 边界缩放 |
| `is_built` | `bool` | 边界是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建边界，初始化数据结构 |
| `update()` | 无 | `None` | 更新边界状态 |
| `reset()` | 无 | `None` | 重置边界到初始状态 |
| `check_collision()` | `Entity` | `bool` | 检查与实体的碰撞 |
| `resolve_collision()` | `Entity` | `None` | 处理与实体的碰撞响应 |

## 继承关系

```
BaseBoundary
├── RigidBoundary
├── ParticleBoundary
└── FluidBoundary
```

```{eval-rst}
.. autoclass:: genesis.engine.boundaries.base_boundary.BaseBoundary
    :members:
    :show-inheritance:
    :undoc-members:
```
