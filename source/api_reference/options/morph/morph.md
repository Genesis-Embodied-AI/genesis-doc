# `gs.morphs.Morph`

## 概述

`Morph` 是 Genesis 中表示实体形态的基类，封装了实体的几何形状和位姿信息。它是所有具体形态类的抽象基类，提供了创建各种实体形态的基础框架。

## 主要功能

- 封装实体的几何形状和位姿信息
- 提供创建各种实体形态的统一接口
- 支持设置实体的初始位置和姿态
- 控制实体的可视化和碰撞属性
- 支持设置实体的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `pos` | tuple | (0.0, 0.0, 0.0) | 实体的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 实体的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 实体的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化实体，仅用于 RigidEntity |
| `collision` | bool | True | 实体是否需要参与碰撞检测，仅用于 RigidEntity |
| `requires_jac_and_IK` | bool | False | 实体是否需要雅可比矩阵和逆运动学计算，仅用于 RigidEntity |
| `is_free` | bool | True | 实体是否可以自由移动，仅用于 RigidEntity |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Morph
```
