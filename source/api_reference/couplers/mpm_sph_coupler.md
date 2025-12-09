# MPMSPHCoupler

`MPMSPHCoupler` 是 MPM（Material Point Method）与 SPH（Smoothed Particle Hydrodynamics）系统之间的耦合器，用于处理 MPM 流体/固体与 SPH 流体之间的交互。

## 功能说明

`MPMSPHCoupler` 类提供了以下核心功能：

- MPM 与 SPH 系统的碰撞检测和响应
- 两种粒子方法之间的数据交换和交互
- 不同粒子系统之间的混合模拟
- 支持多种流体类型之间的交互
- 可调节的耦合参数

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 耦合器在系统中的唯一索引 |
| `uid` | `int` | 耦合器的全局唯一标识符 |
| `name` | `str` | 耦合器的名称 |
| `type` | `str` | 耦合器类型，固定为 "mpm_sph" |
| `mpm_solver` | `MPMSolver` | MPM 求解器 |
| `sph_solver` | `SPHSolver` | SPH 求解器 |
| `iterations` | `int` | 耦合迭代次数 |
| `smoothing_length` | `float` | 粒子平滑长度 |
| `coupling_strength` | `float` | 耦合强度 |
| `is_built` | `bool` | 耦合器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 MPM-SPH 耦合器，初始化连接和数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 MPM-SPH 耦合模拟 |
| `reset()` | 无 | `None` | 重置耦合器到初始状态 |
| `detect_collisions()` | 无 | `list` | 检测 MPM 与 SPH 系统之间的碰撞 |
| `solve_coupling()` | 无 | `None` | 求解 MPM-SPH 耦合 |

## 继承关系

```
BaseCoupler
└── MPMSPHCoupler
```

```{eval-rst}
.. autoclass:: genesis.engine.couplers.mpm_sph_coupler.MPMSPHCoupler
    :members:
    :show-inheritance:
    :undoc-members:
```
