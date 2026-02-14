# FEMSolver

`FEMSolver` 实现了 Finite Element Method (FEM，有限元法)，用于高精度仿真可变形固体。

## 概述

FEM solver：

- Uses tetrahedral mesh elements (使用四面体网格元素)
- Supports various constitutive models (支持多种本构模型)
- Handles large deformations (geometric nonlinearity) (处理大变形，几何非线性)
- GPU-accelerated assembly and solve (GPU 加速的组装和求解)

## 支持的材料

| Material | Description |
|----------|-------------|
| `FEM.Elastic` | Linear/nonlinear elasticity (线性/非线性弹性) |
| `FEM.Muscle` | Active muscle contraction (主动肌肉收缩) |

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    fem_options=gs.options.FEMOptions(
        dt=1e-3,
        damping=0.1,
    ),
)

# Add FEM entity
soft_body = scene.add_entity(
    gs.morphs.Mesh(file="soft_object.obj"),
    material=gs.materials.FEM.Elastic(
        E=1e5,
        nu=0.4,
        rho=1000,
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## 配置

`FEMOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `dt` | float | Internal timestep (内部时间步长) |
| `damping` | float | Rayleigh damping coefficient (瑞利阻尼系数) |
| `iterations` | int | Solver iterations (求解器迭代次数) |

## 边界条件

应用固定的边界条件：

```python
# Fix bottom vertices (固定底部顶点)
soft_body.fix_vertices(z_min=0.01)

# Apply external forces (施加外力)
soft_body.apply_force(vertex_ids, force_vector)
```

## 另请参阅

- {doc}`/api_reference/entity/fem_entity` - FEMEntity
- {doc}`/api_reference/material/fem/index` - FEM 材料
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/fem_options` - 完整选项
