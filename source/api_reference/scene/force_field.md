# `ForceField`

## 概述
`ForceField` 是所有力场的基类，用于在模拟中对物体施加各种类型的力（实际上是加速度场）。

## 主要功能
- 提供统一的接口用于所有类型的力场
- 支持激活/停用力场
- 包含多种预定义的力场类型，如恒定力、风力、点力等
- 支持自定义力场函数

## 继承关系
```
ForceField
├── Constant
├── Wind
├── Point
├── Drag
├── Noise
├── Vortex
├── Turbulence
└── Custom
```

## 使用示例

### 使用恒定力场

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 添加一个球体
sphere = gs.primitives.Sphere(position=(0, 0, 1))
scene.add_entity(sphere)

# 创建并添加恒定力场（恒定加速度）
constant_force = gs.force_fields.Constant(direction=(1, 0, 0), strength=5.0)
scene.add_force_field(constant_force)

# 构建并运行场景
scene.build()
for _ in range(100):
    scene.step()
```

### 使用风力场

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 添加多个球体
for i in range(5):
    sphere = gs.primitives.Sphere(
        position=(i-2, 0, 2),
        radius=0.2
    )
    scene.add_entity(sphere)

# 创建并添加风力场
wind = gs.force_fields.Wind(
    direction=(1, 0, 0),
    strength=3.0,
    turbulence=0.1
)
scene.add_force_field(wind)

# 构建并运行场景
scene.build()
for _ in range(200):
    scene.step()
```

### 使用点力场

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 添加多个球体
for i in range(3):
    for j in range(3):
        sphere = gs.primitives.Sphere(
            position=(i-1, j-1, 2),
            radius=0.15
        )
        scene.add_entity(sphere)

# 创建并添加点力场（吸引力）
point_force = gs.force_fields.Point(
    position=(0, 0, 0),
    strength=-10.0,  # 负值表示吸引力
    falloff=2.0  # 平方反比衰减
)
scene.add_force_field(point_force)

# 构建并运行场景
scene.build()
for _ in range(150):
    scene.step()
```

### 使用自定义力场

```python
import genesis as gs
import numpy as np

# 创建场景
scene = gs.Scene()

# 添加一个球体
sphere = gs.primitives.Sphere(position=(0, 0, 2))
scene.add_entity(sphere)

# 定义自定义力场函数
def custom_force(position, velocity, time):
    # 创建一个随时间变化的正弦力场
    force = np.array([
        np.sin(time * 2.0),
        np.cos(time * 2.0),
        -5.0
    ])
    return force

# 创建并添加自定义力场
custom_ff = gs.force_fields.Custom(force_func=custom_force)
scene.add_force_field(custom_ff)

# 构建并运行场景
scene.build()
for _ in range(200):
    scene.step()
```

```{eval-rst}  
.. automodule:: genesis.engine.force_fields
    :members:
    :show-inheritance:
    :undoc-members:
```