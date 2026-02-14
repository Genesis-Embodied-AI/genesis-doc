# ToolSolver

`ToolSolver` 用于处理与其他物理对象交互的运动学工具和末端执行器。

## 概述

Tool solver 提供以下功能：

- Kinematic motion control (运动学运动控制)
- Collision with other solvers (MPM, FEM, etc.) (与其他 solvers 的碰撞，如 MPM、FEM 等)
- Tool-object interaction (工具-对象交互)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    tool_options=gs.options.ToolOptions(),
)

# Add kinematic tool
tool = scene.add_entity(
    gs.morphs.Mesh(file="tool.obj"),
    material=gs.materials.Tool(),
)

scene.build()

# Kinematically control tool
for i in range(1000):
    tool.set_pos(new_position)
    tool.set_quat(new_orientation)
    scene.step()
```

## 配置

`ToolOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `collision_margin` | float | Collision detection margin (碰撞检测边距) |

## 与其他 Solvers 的交互

Tools 可以与以下对象交互：

- MPM particles (MPM 粒子)
- FEM elements (FEM 元素)
- PBD particles/cloth (PBD 粒子/布料)
- SPH fluids (SPH 流体)

耦合由 coupler 系统自动处理。

## 另请参阅

- {doc}`/api_reference/engine/couplers/index` - 与其他 solvers 的耦合
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/tool_options` - 完整选项
