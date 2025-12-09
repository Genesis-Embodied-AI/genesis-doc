# MPMSolver

`MPMSolver` 是物质点方法（Material Point Method）求解器，用于模拟流体、弹性体、塑性体等复杂物质的物理行为。它结合了拉格朗日和欧拉方法的优点，能够处理大变形和破碎现象。

## 功能说明

`MPMSolver` 类提供了以下核心功能：

- 物质点方法模拟
- 多种材料模型支持（弹性、塑性、流体等）
- 碰撞检测和响应
- 自适应网格和粒子管理
- 高精度物理模拟

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `grid_resolution` | `vector` | 背景网格分辨率 |
| `grid_size` | `vector` | 背景网格大小 |
| `n_particles` | `int` | 物质点数量 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 MPM 求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 MPM 模拟 |
| `reset()` | 无 | `None` | 重置 MPM 求解器到初始状态 |
| `particle_to_grid()` | 无 | `None` | 将粒子数据转换到背景网格 |
| `grid_to_particle()` | 无 | `None` | 将网格数据转换回粒子 |

## 继承关系

```
BaseSolver
└── MPMSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.mpm_solver.MPMSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
