# BaseCoupler

`BaseCoupler` 是 Genesis 引擎中所有耦合器的基类，定义了耦合器的核心接口和生命周期管理。它为不同类型的耦合器提供了统一的架构和行为模式。

## 功能说明

`BaseCoupler` 类提供了以下核心功能：

- 耦合器的基本身份标识和配置
- 耦合器与求解器的连接管理
- 系统间数据交换机制
- 耦合器的生命周期管理
- 统一的耦合求解接口

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 耦合器在系统中的唯一索引 |
| `uid` | `int` | 耦合器的全局唯一标识符 |
| `name` | `str` | 耦合器的名称 |
| `type` | `str` | 耦合器类型（如 "sap", "mpm_pbd", "fem_rigid" 等） |
| `solver1` | `Solver` | 第一个连接的求解器 |
| `solver2` | `Solver` | 第二个连接的求解器 |
| `iterations` | `int` | 耦合迭代次数 |
| `is_built` | `bool` | 耦合器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建耦合器，初始化连接和数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的耦合模拟 |
| `reset()` | 无 | `None` | 重置耦合器到初始状态 |
| `connect_solvers()` | `Solver, Solver` | `None` | 连接两个求解器 |
| `exchange_data()` | 无 | `None` | 在连接的求解器之间交换数据 |
| `solve_coupling()` | 无 | `None` | 求解系统间的耦合 |

## 继承关系

```
BaseCoupler
├── SAPCoupler
├── MPMPBDCoupler
├── MPMSPHCoupler
└── FEMRigidCoupler
```

```{eval-rst}
.. autoclass:: genesis.engine.couplers.base_coupler.BaseCoupler
    :members:
    :show-inheritance:
    :undoc-members:
```
