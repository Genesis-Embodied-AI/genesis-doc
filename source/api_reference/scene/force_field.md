# `ForceField`

## 概述
`ForceField` 是所有力场的基类，用于在模拟中对物体施加各种类型的力（实际上是加速度场）。

## 主要功能
- 提供统一的接口用于所有类型的力场
- 支持激活/停用力场
- 包含多种预定义的力场类型，如恒定力、风力、点力等
- 支持自定义力场函数

## 继承关系
```
ForceField
├── Constant
├── Wind
├── Point
├── Drag
├── Noise
├── Vortex
├── Turbulence
└── Custom
```

```{eval-rst}  
.. automodule:: genesis.engine.force_fields
    :members:
    :show-inheritance:
    :undoc-members:
```