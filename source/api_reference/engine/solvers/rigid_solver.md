# RigidSolver

`RigidSolver` 用于处理刚体动力学仿真，包括铰接体、机器人和刚体对象。

## 概述

RigidSolver 实现了以下功能：

- **Forward dynamics (正向动力学)**: Compute accelerations from forces/torques (从力/力矩计算加速度)
- **Collision detection (碰撞检测)**: GJK, MPR, and support function methods (GJK、MPR 和支持函数方法)
- **Contact resolution (接触解析)**: Impulse-based or iterative constraint solving (基于冲量或迭代约束求解)
- **Joint constraints (关节约束)**: Revolute (旋转), prismatic (移动), ball (球), free joints (自由关节)
- **Articulated bodies (铰接体)**: Multi-body tree structures (URDF, MJCF) (多体树结构)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        enable_collision=True,
        enable_joint_limit=True,
        constraint_solver=gs.constraint_solver.Newton,
    ),
)

# Add rigid entities
plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 1)))

scene.build()

# Control robot
robot.set_dofs_position(target_positions)
robot.set_dofs_velocity(target_velocities)

for i in range(1000):
    scene.step()
```

## 配置

`RigidOptions` 中的关键选项：

| Option | Type | Description |
|--------|------|-------------|
| `enable_collision` | bool | Enable collision detection (启用碰撞检测) |
| `enable_joint_limit` | bool | Enforce joint limits (强制执行关节限制) |
| `constraint_solver` | enum | Solver type (CG, Newton) (求解器类型) |
| `max_contact_per_geom` | int | Maximum contacts per geometry (每个几何体的最大接触数) |
| `contact_resolve_eps` | float | Contact resolution tolerance (接触解析容差) |

## 碰撞检测

RigidSolver 支持多种碰撞检测方法：

- **GJK (Gilbert-Johnson-Keerthi)**: General convex collision (通用凸体碰撞)
- **MPR (Minkowski Portal Refinement)**: Penetration depth (穿透深度)
- **Primitives (基本体)**: Optimized sphere, box, capsule collisions (优化的球体、盒体、胶囊体碰撞)

## 接触解析

两种主要方法：

1. **Impulse-based (基于冲量)**: Direct velocity update (直接速度更新)
2. **Constraint solving (约束求解)**: Iterative optimization (CG, Newton) (迭代优化)

```python
# Use Newton solver for better convergence
rigid_options = gs.options.RigidOptions(
    constraint_solver=gs.constraint_solver.Newton,
    iterations=10,
)
```

## 另请参阅

- {doc}`/api_reference/entity/rigid_entity/index` - RigidEntity
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/rigid_options` - 完整选项
