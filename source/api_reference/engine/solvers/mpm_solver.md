# MPMSolver

`MPMSolver` 实现了 Material Point Method (MPM，物质点法)，用于仿真各种材料，包括弹性固体、颗粒材料、流体和相变。

## 概述

MPM 结合了：

- **Lagrangian particles (拉格朗日粒子)**: Track material points (追踪物质点)
- **Eulerian grid (欧拉网格)**: Solve momentum equations (求解动量方程)
- **Particle-grid transfers (粒子-网格传输)**: MLS-MPM for stability (MLS-MPM 用于稳定性)

## 支持的材料

| Material | Description |
|----------|-------------|
| `MPM.Elastic` | Neo-Hookean elasticity (Neo-Hookean 弹性) |
| `MPM.ElastoPlastic` | Plasticity with yield (带屈服的塑性) |
| `MPM.Sand` | Drucker-Prager granular (Drucker-Prager 颗粒材料) |
| `MPM.Snow` | Snow plasticity (雪的塑性) |
| `MPM.Liquid` | Weakly compressible fluid (弱可压缩流体) |
| `MPM.Muscle` | Active muscle material (主动肌肉材料) |

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    mpm_options=gs.options.MPMOptions(
        dt=1e-4,
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
        grid_density=64,
    ),
)

# Add MPM entity
soft_box = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.2, 0.2, 0.2)),
    material=gs.materials.MPM.Elastic(
        E=1e5,      # Young's modulus (杨氏模量)
        nu=0.3,     # Poisson's ratio (泊松比)
        rho=1000,   # Density (密度)
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## 配置

`MPMOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `dt` | float | Internal timestep (内部时间步长) |
| `lower_bound` | tuple | Grid lower corner (网格下角) |
| `upper_bound` | tuple | Grid upper corner (网格上角) |
| `grid_density` | int | Grid cells per unit (每单位网格单元数) |
| `particle_size` | float | Particle spacing (粒子间距) |

## 网格设置

MPM 需要一个背景网格进行计算：

```python
mpm_options = gs.options.MPMOptions(
    lower_bound=(-2, -2, 0),   # Grid min (网格最小值)
    upper_bound=(2, 2, 4),     # Grid max (网格最大值)
    grid_density=128,          # Resolution (分辨率)
)
```

## 材料参数

### 弹性材料

```python
material = gs.materials.MPM.Elastic(
    E=1e5,       # Young's modulus (Pa) (杨氏模量)
    nu=0.3,      # Poisson's ratio (泊松比)
    rho=1000,    # Density (kg/m^3) (密度)
)
```

### 颗粒材料 (Sand)

```python
material = gs.materials.MPM.Sand(
    E=1e6,
    nu=0.2,
    rho=1500,
    friction_angle=30,  # degrees (摩擦角，单位：度)
)
```

## 另请参阅

- {doc}`/api_reference/entity/mpm_entity` - MPMEntity
- {doc}`/api_reference/material/mpm/index` - MPM 材料
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/mpm_options` - 完整选项
