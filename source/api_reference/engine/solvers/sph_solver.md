# SPHSolver

`SPHSolver` 实现了 Smoothed Particle Hydrodynamics (SPH，光滑粒子流体动力学)，用于流体仿真。

## 概述

SPH 使用粒子来近似流体动力学：

- Pressure forces from density (来自密度的压力)
- Viscosity forces from velocity differences (来自速度差的粘性力)
- Surface tension (optional) (表面张力，可选)
- Free surface handling (自由表面处理)

## 支持的材料

| Material | Description |
|----------|-------------|
| `SPH.Liquid` | General liquid simulation (通用液体仿真) |

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sph_options=gs.options.SPHOptions(
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
        particle_size=0.02,
    ),
)

# Add fluid
fluid = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.4, 0.4, 0.4)),
    material=gs.materials.SPH.Liquid(
        rho=1000,     # Density (密度)
        viscosity=0.01,
    ),
)

# Add rigid container
container = scene.add_entity(gs.morphs.Box(
    pos=(0, 0, 0.5),
    size=(0.5, 0.5, 0.5),
    is_rigid=True,
    vis_mode="collision",
))

scene.build()

for i in range(1000):
    scene.step()
```

## 配置

`SPHOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `lower_bound` | tuple | Domain lower corner (域下角) |
| `upper_bound` | tuple | Domain upper corner (域上角) |
| `particle_size` | float | Particle spacing (粒子间距) |
| `dt` | float | Internal timestep (内部时间步长) |

## 参数

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `rho` | Rest density (静止密度) | 1000 kg/m^3 (water) |
| `viscosity` | Dynamic viscosity (动力粘度) | 0.001-0.1 |
| `stiffness` | Pressure stiffness (压力刚度) | 1000-10000 |

## 另请参阅

- {doc}`/api_reference/entity/sph_entity` - SPHEntity
- {doc}`/api_reference/material/sph/index` - SPH 材料
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sph_options` - 完整选项
