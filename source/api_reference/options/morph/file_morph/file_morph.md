# `gs.morphs.FileMorph`

## 概述

`FileMorph` 是 Genesis 中用于从文件加载形态的基类。它提供了从各种文件格式加载模型和形态的接口，是创建复杂场景和对象的基础。

## 主要功能

- 从各种文件格式加载形态
- 支持设置加载模型的位置和姿态
- 控制模型的可视化和碰撞属性
- 提供统一的接口来加载不同格式的文件
- 支持设置模型的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 模型的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 模型的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 模型的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化模型，仅用于 RigidEntity |
| `collision` | bool | True | 模型是否需要参与碰撞检测，仅用于 RigidEntity |
| `requires_jac_and_IK` | bool | False | 模型是否需要雅可比矩阵和逆运动学计算，仅用于 RigidEntity |
| `fixed` | bool | False | 是否固定实体的基链接，仅用于 RigidEntity |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |


```{eval-rst}  
.. autoclass:: genesis.options.morphs.FileMorph
```
