# SAPCoupler

`SAPCoupler` 是分离轴原理（Separating Axis Principle）耦合器，用于处理刚体与其他物理系统之间的碰撞和交互。它是 Genesis 引擎中最常用的耦合器之一。

## 功能说明

`SAPCoupler` 类提供了以下核心功能：

- 刚体与其他系统（如 MPM、PBD、FEM 等）的碰撞检测
- 分离轴原理的高效碰撞检测算法
- 碰撞响应和接触力计算
- 支持多种几何形状的碰撞
- 可调节的碰撞参数

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 耦合器在系统中的唯一索引 |
| `uid` | `int` | 耦合器的全局唯一标识符 |
| `name` | `str` | 耦合器的名称 |
| `type` | `str` | 耦合器类型，固定为 "sap" |
| `solver1` | `Solver` | 第一个连接的求解器（通常是刚体求解器） |
| `solver2` | `Solver` | 第二个连接的求解器 |
| `iterations` | `int` | 耦合迭代次数 |
| `friction` | `float` | 碰撞摩擦系数 |
| `restitution` | `float` | 碰撞弹性恢复系数 |
| `tolerance` | `float` | 碰撞检测公差 |
| `is_built` | `bool` | 耦合器是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建 SAP 耦合器，初始化碰撞检测数据结构 |
| `step()` | 无 | `None` | 执行一个时间步的 SAP 耦合模拟 |
| `reset()` | 无 | `None` | 重置耦合器到初始状态 |
| `detect_collisions()` | 无 | `list` | 检测刚体与其他系统之间的碰撞 |
| `solve_contacts()` | `list` | `None` | 求解碰撞接触点和接触力 |

## 继承关系

```
BaseCoupler
└── SAPCoupler
```

```{eval-rst}
.. autoclass:: genesis.engine.couplers.sap_coupler.SAPCoupler
    :members:
    :show-inheritance:
    :undoc-members:
```
