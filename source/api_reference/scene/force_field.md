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

## 力场类型详情

### 1. Constant（恒定力场）

**功能说明**：
恒定力场在所有空间点施加方向和大小恒定的加速度。它模拟了均匀力场，如重力场（在小范围内可近似为恒定力场）。

**主要参数**：
- `direction`：力场的方向向量，必须是归一化的三维向量
- `strength`：力场的强度（加速度值，单位：m/s²）
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟重力场（方向向下，强度约为9.8 m/s²）
- 施加恒定的推进力或拉力
- 测试物体在均匀力场中的运动

### 2. Wind（风力场）

**功能说明**：
风力场模拟了自然界中的风，具有基本方向和强度，同时可以添加湍流效果以模拟风的不规则性。

**主要参数**：
- `direction`：主风向向量，必须是归一化的三维向量
- `strength`：基础风速强度（m/s²）
- `turbulence`：湍流强度，0表示完全均匀的风，1表示最强的湍流效果
- `turbulence_scale`：湍流尺度，控制湍流涡流的大小
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟自然风环境
- 测试结构在风中的稳定性
- 产生飘动或摇晃的效果

### 3. Point（点力场）

**功能说明**：
点力场从一个点源向外辐射力（或向内吸引），力的大小随距离变化。

**主要参数**：
- `position`：点力场的源位置（三维向量）
- `strength`：力场强度，正值表示排斥力，负值表示吸引力
- `falloff`：衰减指数，控制力随距离减弱的速率（通常为2表示平方反比衰减）
- `radius`：力场影响的最大半径，超出此半径的物体不受影响
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟万有引力（falloff=2）
- 创建吸引力或排斥力源
- 模拟爆炸或冲击效果

### 4. Drag（阻力场）

**功能说明**：
阻力场施加与物体运动方向相反的力，模拟流体阻力或空气阻力。

**主要参数**：
- `coefficient`：阻力系数，控制阻力的强度
- `exponent`：速度指数，1表示线性阻力（粘性阻力），2表示二次阻力（惯性阻力）
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟空气阻力
- 模拟物体在水中的运动
- 使运动物体自然减速

### 5. Noise（噪声力场）

**功能说明**：
噪声力场使用Perlin或Simplex噪声生成空间变化的力场，创造自然、无规则的运动模式。

**主要参数**：
- `scale`：噪声的空间尺度，控制力场变化的频率
- `strength`：噪声力场的强度
- `octaves`：噪声的八度数量，控制力场的细节丰富程度
- `persistence`：噪声的持续性，控制高八度噪声的影响程度
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟自然水流或气流
- 产生复杂的流体运动模式
- 创建有机、自然的运动效果

### 6. Vortex（涡流力场）

**功能说明**：
涡流力场创建一个旋转的力场，模拟漩涡或龙卷风效果。

**主要参数**：
- `position`：涡流中心位置
- `axis`：涡流旋转轴方向
- `strength`：涡流强度
- `radius`：涡流影响半径
- `active`：力场是否激活，默认为True

**典型应用**：
- 模拟龙卷风
- 创建漩涡或漩涡效果
- 产生旋转的流体运动

### 7. Turbulence（湍流力场）

**功能说明**：
湍流力场在基本力场的基础上添加湍流扰动，增强真实感。

**主要参数**：
- `base_force`：基础力场（可选）
- `strength`：湍流强度
- `scale`：湍流尺度
- `octaves`：噪声八度数量
- `active`：力场是否激活，默认为True

**典型应用**：
- 增强风力或水流的真实感
- 模拟复杂的流体动力学效果
- 产生更自然的运动模式

### 8. Custom（自定义力场）

**功能说明**：
自定义力场允许用户通过Python函数定义任意复杂的力场行为，提供最大的灵活性。

**主要参数**：
- `force_func`：用户定义的力场函数，接收位置、速度和时间参数，返回三维力向量
- `active`：力场是否激活，默认为True

**典型应用**：
- 实现特殊的物理效果
- 模拟复杂的力场交互
- 研究自定义物理现象

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