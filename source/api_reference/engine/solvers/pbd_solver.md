# PBDSolver

`PBDSolver` 实现了 Position Based Dynamics (PBD，基于位置的动力学)，用于以快速、稳定的性能仿真布料、软体和粒子系统。

## 概述

PBD 的工作原理：

- Predicting particle positions (预测粒子位置)
- Projecting constraint violations (投影约束违反)
- Iteratively correcting positions (迭代校正位置)
- Computing velocities from position change (根据位置变化计算速度)

Advantages (优势)：
- **Stability (稳定性)**: Unconditionally stable (无条件稳定)
- **Speed (速度)**: Fast iterative solving (快速迭代求解)
- **Controllability (可控性)**: Direct position control (直接位置控制)

## 支持的材料

| Material | Description |
|----------|-------------|
| `PBD.Cloth` | Cloth/fabric simulation (布料/织物仿真) |
| `PBD.Elastic` | Soft elastic bodies (软弹性体) |
| `PBD.Particle` | Particle systems (粒子系统) |
| `PBD.Liquid` | Position-based fluids (基于位置的流体) |

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    pbd_options=gs.options.PBDOptions(
        iterations=10,
        damping=0.99,
    ),
)

# Add cloth
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_stiffness=0.9,
        bend_stiffness=0.1,
    ),
)

# Fix top edge
cloth.fix_vertices(y_max=0.99)

scene.build()

for i in range(1000):
    scene.step()
```

## 配置

`PBDOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `iterations` | int | Constraint iterations (约束迭代次数) |
| `damping` | float | Velocity damping (速度阻尼) |
| `gravity` | tuple | Override gravity (覆盖重力) |

## 约束类型

PBD 使用多种约束：

- **Distance constraints (距离约束)**: Maintain edge lengths (保持边长)
- **Bending constraints (弯曲约束)**: Resist folding (抵抗折叠)
- **Volume constraints (体积约束)**: Preserve volume (保持体积)
- **Collision constraints (碰撞约束)**: Handle contacts (处理接触)

## 布料示例

```python
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_stiffness=0.95,   # Resist stretching (抗拉伸)
        bend_stiffness=0.05,      # Allow bending (允许弯曲)
        thickness=0.01,           # Collision thickness (碰撞厚度)
    ),
)
```

## 另请参阅

- {doc}`/api_reference/entity/pbd_entity/index` - PBD 实体
- {doc}`/api_reference/material/pbd/index` - PBD 材料
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/pbd_options` - 完整选项
