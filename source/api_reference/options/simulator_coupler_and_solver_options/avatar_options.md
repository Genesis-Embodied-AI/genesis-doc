# `gs.options.AvatarOptions`

## 概述

`AvatarOptions` 是 Genesis 中配置 AvatarSolver 的选项类，用于设置与虚拟角色相关的模拟参数。AvatarEntity 类似于 RigidEntity，但没有内部物理特性，主要用于控制虚拟角色的碰撞和逆运动学（IK）行为。

## 主要功能

- 配置 AvatarSolver 的时间步长
- 启用或禁用碰撞检测
- 设置自碰撞和相邻碰撞的参数
- 配置逆运动学（IK）的目标数量
- 限制动态约束的最大数量

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `dt` | Optional[float] | None | 每个模拟步骤的时间持续时间（秒）。如果为 None，则从 `SimOptions` 继承。 |
| `enable_collision` | bool | False | 是否启用碰撞检测。 |
| `enable_self_collision` | bool | False | 是否启用每个实体内部的自碰撞。 |
| `enable_adjacent_collision` | bool | False | 是否启用每个实体内部连续父子身体对之间的碰撞。 |
| `max_collision_pairs` | int | 300 | 最大碰撞对数量。 |
| `IK_max_targets` | int | 6 | 最大逆运动学（IK）目标数量。增加此值不会影响IK求解速度，但会增加内存使用。 |
| `max_dynamic_constraints` | int | 8 | 动态约束（如吸盘）的最大数量。 |

```{eval-rst}  
.. autoclass:: genesis.options.solvers.AvatarOptions
```
