# `gs.morphs.URDF`

## 概述

`URDF` 类用于从URDF (Unified Robot Description Format) 文件加载机器人模型，是 `FileMorph` 类的子类。URDF是ROS机器人操作系统中常用的机器人描述格式，包含机器人的关节、连杆、传感器和执行器信息。

## 主要功能

- 从URDF文件加载完整的机器人模型
- 支持设置机器人的初始位置和姿态
- 控制机器人的可视化和碰撞属性
- 支持合并固定链接以简化模型
- 可配置是否优先使用URDF文件中定义的材质
- 支持设置机器人的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的URDF文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 机器人的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 机器人的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 机器人的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化机器人模型 |
| `collision` | bool | True | 机器人是否需要参与碰撞检测 |
| `requires_jac_and_IK` | bool | False | 机器人是否需要雅可比矩阵和逆运动学计算 |
| `fixed` | bool | False | 是否固定机器人的基链接 |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `prioritize_urdf_material` | bool | True | 是否优先使用URDF文件中定义的材质 |
| `merge_fixed_links` | bool | True | 是否合并机器人的固定链接以简化模型 |
| `decompose_robot_error_threshold` | float | 0.0001 | 机器人分解时的误差阈值 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.URDF
```
