# `gs.morphs.Primitive`

## 概述

`Primitive` 是 Genesis 中用于创建基本几何形状的形态类。它提供了创建各种基本几何体（如立方体、球体、圆柱体等）的接口，是构建简单场景和对象的基础。

## 主要功能

- 创建各种基本几何形状
- 支持设置几何体的尺寸和属性
- 控制几何体的可视化和碰撞属性
- 支持设置几何体的自由度和运动约束
- 提供统一的接口来创建不同类型的基本几何体

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `pos` | tuple | (0.0, 0.0, 0.0) | 几何体的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 几何体的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 几何体的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化几何体，仅用于 RigidEntity |
| `collision` | bool | True | 几何体是否需要参与碰撞检测，仅用于 RigidEntity |
| `requires_jac_and_IK` | bool | False | 几何体是否需要雅可比矩阵和逆运动学计算，仅用于 RigidEntity |
| `fixed` | bool | False | 是否固定实体的基链接，仅用于 RigidEntity |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Primitive
```
