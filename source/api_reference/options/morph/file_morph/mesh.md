# `gs.morphs.Mesh`

## 概述

`Mesh` 类用于从文件加载3D网格模型，是 `FileMorph` 类的子类。它支持加载各种常见的3D模型格式，如OBJ、STL、PLY等，是创建复杂3D对象的基础。

## 主要功能

- 从各种3D模型文件格式加载网格
- 支持设置模型的位置和姿态
- 控制模型的可视化和碰撞属性
- 可用于刚体实体和其他需要网格形状的实体类型
- 支持设置网格的自由度和运动约束

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `file_path` | str | None | 要加载的3D模型文件路径 |
| `pos` | tuple | (0.0, 0.0, 0.0) | 模型的初始位置 (x, y, z) |
| `euler` | tuple | (0.0, 0.0, 0.0) | 模型的初始欧拉角 (roll, pitch, yaw)，使用弧度制 |
| `quat` | tuple | None | 模型的初始四元数 (w, x, y, z)，如果指定则忽略 euler 参数 |
| `visualization` | bool | True | 是否需要可视化模型，仅用于 RigidEntity |
| `collision` | bool | True | 模型是否需要参与碰撞检测，仅用于 RigidEntity |
| `requires_jac_and_IK` | bool | False | 模型是否需要雅可比矩阵和逆运动学计算，仅用于 RigidEntity |
| `fixed` | bool | False | 是否固定实体的基链接，仅用于 RigidEntity |
| `contype` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `conaffinity` | int | 0xFFFF | 用于接触过滤的 32 位整数位掩码 |
| `order` | int | 1 | FEM网格的阶数，仅用于 FEMEntity |
| `mindihedral` | int | 10 | 四面体化过程中的最小二面角（度），仅用于需要四面体化的体积实体 |
| `minratio` | float | 1.1 | 四面体化过程中的最小四面体质量比，仅用于需要四面体化的体积实体 |
| `nobisect` | bool | True | 是否在四面体化过程中禁用二分法，仅用于需要四面体化的体积实体 |
| `quality` | bool | True | 是否在四面体化过程中提高质量，仅用于需要四面体化的体积实体 |
| `maxvolume` | float | -1.0 | 最大四面体体积，-1.0 表示无限制，仅用于需要四面体化的体积实体 |
| `verbose` | int | 0 | 四面体化过程中的详细程度，仅用于需要四面体化的体积实体 |
| `force_retet` | bool | False | 是否强制重新四面体化，仅用于需要四面体化的体积实体 |
| `decompose_robot_error_threshold` | float | 0.0001 | 机器人分解时的误差阈值 |

```{eval-rst}  
.. autoclass:: genesis.options.morphs.Mesh
```
