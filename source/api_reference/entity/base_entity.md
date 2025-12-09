# BaseEntity

`BaseEntity` 是 Genesis 引擎中所有实体类的基类，定义了所有实体共享的核心属性和方法。它为不同类型的实体（如刚体、变形体、流体等）提供了统一的接口和基础架构。

## 功能说明

`BaseEntity` 类提供了以下核心功能：

- 实体的基本身份标识（idx、uid、name）
- 与场景和模拟器的关联
- 物理求解器的连接
- 材质和形态的管理
- 实体构建和初始化机制
- 统一的实体生命周期管理

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 实体在场景中的唯一索引 |
| `uid` | `int` | 实体的全局唯一标识符 |
| `name` | `str` | 实体的名称 |
| `scene` | `Scene` | 实体所属的场景对象 |
| `sim` | `Simulator` | 管理实体的模拟器对象 |
| `solver` | `Solver` | 处理实体物理模拟的求解器 |
| `material` | `Material` | 实体的物理材质属性 |
| `morph` | `Morph` | 实体的几何形态配置 |
| `surface` | `Surface` | 实体的渲染表面属性 |
| `is_built` | `bool` | 实体是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建实体，初始化物理属性和约束 |
| `update()` | 无 | `None` | 更新实体状态 |
| `reset()` | 无 | `None` | 重置实体到初始状态 |
| `remove()` | 无 | `None` | 从场景中移除实体 |

## 继承关系

`BaseEntity` 是所有实体类的基类，以下是主要的继承关系：

```
BaseEntity
├── RigidEntity
├── AvatarEntity
├── MPMEntity
├── PBD2DEntity
├── PBD3DEntity
├── FEMEntity
├── SPHEntity
├── HybridEntity
├── Emitter
├── DroneEntity
├── ToolEntity
└── SFEntity
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.base_entity.BaseEntity
    :members:
    :show-inheritance:
    :undoc-members:
```
