# `gs.morphs.Terrain`

## 概述

`Terrain` 类用于从文件加载地形模型，是 `FileMorph` 类的子类。它支持加载各种地形文件格式，用于创建复杂的物理模拟环境。

## 主要功能

- 从地形文件加载地形模型
- 支持设置地形的位置和姿态
- 控制地形的可视化和碰撞属性
- 可用于创建复杂的物理模拟环境
- 支持设置地形的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的地形文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 地形的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 地形的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 地形的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化地形 |
| `collision` | bool | True | 地形是否需要参与碰撞检测 |
| `requires_jac_and_IK` | bool | False | 地形是否需要雅可比矩阵和逆运动学计算 |
| `fixed` | bool | True | 是否固定地形，使其不可移动 |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `merge_fixed_links` | bool | True | 是否合并地形的固定链接以简化模型 |
| `decompose_robot_error_threshold` | float | 0.0001 | 地形分解时的误差阈值 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Terrain
```
