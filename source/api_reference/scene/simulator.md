# `Simulator`

`Simulator` 是 Genesis 引擎中用于执行物理模拟的核心类，它包含了多个物理求解器，负责处理实体的物理行为和相互作用。

## 功能说明

- 管理多个物理求解器（如刚体、流体、可变形体等）
- 执行物理模拟的时间步长更新
- 处理实体之间的碰撞和接触
- 支持求解器选项的配置

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `gravity` | list | 重力加速度向量 |
| `dt` | float | 模拟时间步长 |
| `substeps` | int | 每个时间步的子步数 |
| `entities` | list | 模拟器中的所有实体列表 |
| `solvers` | list | 模拟器中的所有求解器列表 |
| `active_solvers` | list | 当前激活的求解器列表 |
| `cur_t` | float | 当前模拟时间 |
| `cur_step_global` | int | 当前全局步数 |

```{eval-rst}  
.. autoclass:: genesis.engine.simulator.Simulator
    :members:
    :undoc-members:
```