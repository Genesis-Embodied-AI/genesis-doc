# `gs.morphs.MJCF`

## 概述

`MJCF` 类用于从MJCF (MuJoCo XML Format) 文件加载模型，是 `FileMorph` 类的子类。MJCF是MuJoCo物理引擎使用的XML格式，用于定义物理模拟场景、机器人模型和环境。

## 主要功能

- 从MJCF文件加载完整的物理模拟模型
- 支持设置模型的初始位置和姿态
- 控制模型的可视化和碰撞属性
- 支持合并固定链接以简化模型
- 可配置是否优先使用MJCF文件中定义的材质
- 支持设置模型的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的MJCF文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 模型的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 模型的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 模型的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化模型 |
| `collision` | bool | True | 模型是否需要参与碰撞检测 |
| `requires_jac_and_IK` | bool | False | 模型是否需要雅可比矩阵和逆运动学计算 |
| `fixed` | bool | False | 是否固定模型的基链接 |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `merge_fixed_links` | bool | True | 是否合并模型的固定链接以简化模型 |
| `decompose_robot_error_threshold` | float | 0.0001 | 模型分解时的误差阈值 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.MJCF
```
