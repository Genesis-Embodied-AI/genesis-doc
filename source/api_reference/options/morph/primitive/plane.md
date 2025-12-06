# `gs.morphs.Plane`

## 概述

`Plane` 类用于创建平面形状的几何体，是 `Primitive` 类的子类。它提供了创建具有指定尺寸的平面的接口，通常用于构建地面或其他平面表面。

## 主要功能

- 创建指定尺寸的平面
- 支持设置平面的位置和姿态
- 控制平面的可视化和碰撞属性
- 可用于刚体实体和其他需要平面形状的实体类型
- 支持设置平面的纹理平铺大小

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `pos` | tuple | (0.0, 0.0, 0.0) | 平面的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 平面的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 平面的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化平面，仅用于 RigidEntity |
| `collision` | bool | True | 平面是否需要参与碰撞检测，仅用于 RigidEntity |
| `requires_jac_and_IK` | bool | False | 平面是否需要雅可比矩阵和逆运动学计算，仅用于 RigidEntity |
| `fixed` | bool | False | 是否固定实体的基链接，仅用于 RigidEntity |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `plane_size` | tuple | (1e3, 1e3) | 平面的尺寸 (width, depth)，默认值很大以模拟无限平面 |
| `tile_size` | tuple | (1, 1) | 每个纹理平铺的大小，用于可视化 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Plane
```
