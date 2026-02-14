# SFSolver

`SFSolver` (String/Fiber，绳/纤维) 用于处理绳索、缆线和头发等一维结构的仿真。

## 概述

SF solver 仿真：

- Inextensible constraints (不可伸长约束)
- Bending resistance (弯曲阻力)
- Twist resistance (扭转阻力)
- Contact with other objects (与其他对象的接触)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sf_options=gs.options.SFOptions(
        iterations=20,
    ),
)

# Add rope/cable
rope = scene.add_entity(
    gs.morphs.Mesh(file="rope.obj"),
    material=gs.materials.SF.Rope(
        stretch_stiffness=1.0,
        bend_stiffness=0.1,
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## 配置

`SFOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `iterations` | int | Constraint iterations (约束迭代次数) |
| `damping` | float | Velocity damping (速度阻尼) |

## 另请参阅

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sf_options` - 完整选项
