# `gs.options.RigidOptions`

## 概述

`RigidOptions` 是 Genesis 中配置刚体动力学求解器的选项类，用于设置刚体模拟的参数，如碰撞检测、约束求解、积分器类型、休眠机制等。该类提供了丰富的参数来控制刚体模拟的行为和性能。

## 主要功能

- 配置刚体模拟的时间步长和重力
- 控制碰撞检测行为（自碰撞、相邻碰撞、碰撞对数量等）
- 设置约束求解器参数（迭代次数、容差、求解器类型等）
- 配置积分器类型
- 启用/禁用休眠机制以提高性能
- 支持批处理信息输出
- 提供与Mujoco兼容性选项
- 支持GJK碰撞检测算法

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `gravity` | Optional[tuple] | None | 重力加速度（N/kg）。如果为 None，则从 `SimOptions` 继承。 |
| `enable_collision` | bool | True | 是否启用碰撞检测。 |
| `enable_joint_limit` | bool | True | 是否启用关节限制。 |
| `enable_self_collision` | bool | True | 是否启用自碰撞检测。 |
| `enable_adjacent_collision` | bool | False | 是否启用相邻碰撞检测。 |
| `disable_constraint` | bool | False | 是否禁用约束。 |
| `max_collision_pairs` | int | 300 | 最大碰撞对数量。 |
| `integrator` | enum | approximate_implicitfast | 积分器类型。 |
| `IK_max_targets` | int | 6 | 逆运动学的最大目标数量。 |
| `batch_links_info` | Optional[bool] | False | 是否启用批量链接信息输出。 |
| `batch_joints_info` | Optional[bool] | False | 是否启用批量关节信息输出。 |
| `batch_dofs_info` | Optional[bool] | False | 是否启用批量自由度信息输出。 |
| `constraint_solver` | enum | Newton | 约束求解器类型。 |
| `iterations` | int | 50 | 约束求解器的最大迭代次数。 |
| `tolerance` | float | 1e-08 | 约束求解器的容差。 |
| `ls_iterations` | int | 50 | 线性搜索的最大迭代次数。 |
| `ls_tolerance` | float | 0.01 | 线性搜索的容差。 |
| `sparse_solve` | bool | False | 是否使用稀疏求解。 |
| `contact_resolve_time` | Optional[float] | None | 接触分辨率时间。 |
| `constraint_timeconst` | float | 0.01 | 约束时间常数。 |
| `use_contact_island` | bool | False | 是否使用接触岛。 |
| `box_box_detection` | bool | True | 是否启用盒对盒检测。 |
| `use_hibernation` | bool | False | 是否启用休眠机制。注意：休眠功能尚未经过充分测试，将很快完全支持。 |
| `hibernation_thresh_vel` | float | 0.001 | 休眠速度阈值。 |
| `hibernation_thresh_acc` | float | 0.01 | 休眠加速度阈值。 |
| `max_dynamic_constraints` | int | 8 | 最大动态约束数量。 |
| `enable_multi_contact` | bool | True | 是否启用多接触点。 |
| `enable_mujoco_compatibility` | bool | False | 是否启用Mujoco兼容性。 |
| `use_gjk_collision` | bool | True | 是否使用GJK（ Gilbert-Johnson-Keerthi）碰撞检测算法代替MPR（ Minkowski Portal Refinement）。 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.RigidOptions
```
