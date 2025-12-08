# `SFEntity`

## 概述

`SFEntity` 是 Genesis 引擎中用于模拟烟雾/火焰（Smoke/Fire）效果的实体类。目前，烟雾/火焰功能主要通过 `SFOptions` 类进行配置，用于设置烟雾/火焰模拟的参数，如时间步长、分辨率、求解器迭代次数、衰减系数、温度阈值以及入口参数等。

## 主要功能

- 模拟烟雾和火焰的物理行为
- 支持通过 `SFOptions` 配置模拟参数
- 可设置入口位置、速度和强度
- 支持温度阈值和衰减系数调整
- 与其他实体类型（如刚体、软体）进行交互

## 使用示例

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 配置SF求解器选项
scene.options.solver.sf_options.dt = 0.01
scene.options.solver.sf_options.res = 256
scene.options.solver.sf_options.decay = 0.98
scene.options.solver.sf_options.inlet_pos = (0.5, 0.0, 0.1)
scene.options.solver.sf_options.inlet_vel = (0, 0, 2)
scene.options.solver.sf_options.inlet_s = 500.0

# 添加一个简单的刚体实体作为障碍物
scene.add_entity(type='rigid', mesh=gs.Mesh.create_box(size=[0.5, 0.5, 1.0]), pos=[0.0, 0.0, 0.5])

# 构建并运行模拟
scene.build()
for i in range(200):
    scene.step()
    if i % 10 == 0:
        scene.render()

scene.release()
```

```{eval-rst}
.. note::
    烟雾/火焰实体的完整接口正在开发中。目前，烟雾/火焰模拟主要通过配置 `SFOptions` 来实现。

.. autoclass:: genesis.options.solvers.SFOptions
    :members:
    :show-inheritance:
    :undoc-members:
```