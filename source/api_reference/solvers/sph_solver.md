# SPHSolver

`SPHSolver` 是光滑粒子流体动力学（Smoothed Particle Hydrodynamics）求解器，用于模拟流体的流动、飞溅和破碎现象。它通过粒子之间的相互作用力来模拟流体行为。

## 功能说明

`SPHSolver` 类提供了以下核心功能：

- 光滑粒子流体动力学模拟
- 不可压缩流体模拟
- 表面张力和粘性处理
- 碰撞检测和响应
- 高效的粒子邻居搜索

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 求解器在系统中的唯一索引 |
| `uid` | `int` | 求解器的全局唯一标识符 |
| `name` | `str` | 求解器的名称 |
| `dt` | `float` | 时间步长 |
| `gravity` | `vector` | 重力加速度 |
| `n_particles` | `int` | 流体粒子数量 |
| `h` | `float` | 光滑长度 |
| `rest_density` | `float` | 流体静止密度 |
| `viscosity` | `float` | 流体粘性系数 |
| `surface_tension` | `float` | 表面张力系数 |
| `is_built` | `bool` | 求解器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 SPH 求解器，初始化数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 SPH 模拟 |
| `reset()` | 无 | `None` | 重置 SPH 求解器到初始状态 |
| `find_neighbors()` | 无 | `None` | 查找粒子邻居 |
| `compute_densities()` | 无 | `None` | 计算粒子密度 |
| `compute_forces()` | 无 | `None` | 计算粒子间作用力 |

## 继承关系

```
BaseSolver
└── SPHSolver
```

```{eval-rst}
.. autoclass:: genesis.engine.solvers.sph_solver.SPHSolver
    :members:
    :show-inheritance:
    :undoc-members:
```
