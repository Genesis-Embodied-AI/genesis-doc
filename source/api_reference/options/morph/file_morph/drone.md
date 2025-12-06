# `gs.morphs.Drone`

## 概述

`Drone` 类用于从文件加载无人机模型，是 `FileMorph` 类的子类。它专门用于无人机模型，提供了特殊的参数来配置无人机的螺旋桨、电机和控制相关属性。

## 主要功能

- 从文件加载无人机模型
- 支持设置无人机的初始位置和姿态
- 控制无人机的可视化和碰撞属性
- 可配置螺旋桨的链接名称和属性
- 支持合并固定链接以简化模型
- 可配置是否优先使用模型文件中定义的材质

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的无人机模型文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 无人机的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 无人机的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 无人机的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化无人机模型 |
| `collision` | bool | True | 无人机是否需要参与碰撞检测 |
| `requires_jac_and_IK` | bool | False | 无人机是否需要雅可比矩阵和逆运动学计算 |
| `fixed` | bool | False | 是否固定无人机，使其不可移动 |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `merge_fixed_links` | bool | True | 是否合并无人机的固定链接以简化模型 |
| `prioritize_urdf_material` | bool | True | 是否优先使用模型文件中定义的材质 |
| `propellers_link_name` | list | [] | 无人机螺旋桨的链接名称列表 |
| `decompose_robot_error_threshold` | float | 0.0001 | 无人机分解时的误差阈值 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Drone
```
