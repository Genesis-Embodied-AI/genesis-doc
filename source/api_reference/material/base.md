# MaterialBase

`MaterialBase` 是 Genesis 引擎中所有材质类的基类，定义了所有材质共享的核心属性和方法。它为不同类型的材质（如刚体材质、变形体材质、流体材质等）提供了统一的接口和基础架构。

## 功能说明

`MaterialBase` 类提供了以下核心功能：

- 材质的基本身份标识和分类
- 共享物理属性的定义（如密度、摩擦系数等）
- 材质参数的初始化和验证
- 与物理求解器的兼容机制
- 统一的材质属性访问接口

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 材质在材质库中的唯一索引 |
| `uid` | `int` | 材质的全局唯一标识符 |
| `name` | `str` | 材质的名称 |
| `type` | `str` | 材质类型（如 "rigid", "elastic", "liquid" 等） |
| `density` | `float` | 材质的密度 |
| `friction` | `float` | 材质的摩擦系数 |
| `restitution` | `float` | 材质的弹性恢复系数 |
| `is_built` | `bool` | 材质是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建材质，初始化物理参数 |
| `update()` | 无 | `None` | 更新材质属性 |
| `reset()` | 无 | `None` | 重置材质到初始状态 |

## 继承关系

`MaterialBase` 是所有材质类的基类，以下是主要的继承关系：

```
MaterialBase
├── RigidMaterial
├── AvatarMaterial
├── FEMMaterial
│   ├── FEMElasticMaterial
│   └── FEMMuscleMaterial
├── MPMMaterial
│   ├── MPMElasticMaterial
│   ├── MPMElastoPlasticMaterial
│   ├── MPMLiquidMaterial
│   ├── MPMMuscleMaterial
│   ├── MPMSandMaterial
│   └── MPMSnowMaterial
├── PBDMaterial
│   ├── PBDClothMaterial
│   ├── PBDElasticMaterial
│   ├── PBDLiquidMaterial
│   └── PBDParticleMaterial
└── SPHMaterial
    └── SPHLiquidMaterial
```

```{eval-rst}
.. autoclass:: genesis.engine.materials.base.MaterialBase
    :members:
    :show-inheritance:
    :undoc-members:
```
