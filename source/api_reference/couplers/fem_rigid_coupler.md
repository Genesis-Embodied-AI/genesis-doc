# FEMRigidCoupler

`FEMRigidCoupler` 是 FEM（Finite Element Method）与 Rigid Body 系统之间的耦合器，用于处理 FEM 弹性体与刚体之间的碰撞和交互。

## 功能说明

`FEMRigidCoupler` 类提供了以下核心功能：

- FEM 与刚体系统的碰撞检测和响应
- 有限元网格与刚体几何之间的交互
- 接触力计算和传递
- 支持弹性体与刚体的复杂交互
- 可调节的耦合参数

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 耦合器在系统中的唯一索引 |
| `uid` | `int` | 耦合器的全局唯一标识符 |
| `name` | `str` | 耦合器的名称 |
| `type` | `str` | 耦合器类型，固定为 "fem_rigid" |
| `fem_solver` | `FEMSolver` | FEM 求解器 |
| `rigid_solver` | `RigidSolver` | 刚体求解器 |
| `iterations` | `int` | 耦合迭代次数 |
| `friction` | `float` | 碰撞摩擦系数 |
| `restitution` | `float` | 碰撞弹性恢复系数 |
| `is_built` | `bool` | 耦合器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 FEM-Rigid 耦合器，初始化连接和数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 FEM-Rigid 耦合模拟 |
| `reset()` | 无 | `None` | 重置耦合器到初始状态 |
| `detect_collisions()` | 无 | `list` | 检测 FEM 与刚体系统之间的碰撞 |
| `solve_contacts()` | `list` | `None` | 求解碰撞接触点和接触力 |

## 继承关系

```
BaseCoupler
└── FEMRigidCoupler
```

```{eval-rst}
.. autoclass:: genesis.engine.couplers.fem_rigid_coupler.FEMRigidCoupler
    :members:
    :show-inheritance:
    :undoc-members:
```
