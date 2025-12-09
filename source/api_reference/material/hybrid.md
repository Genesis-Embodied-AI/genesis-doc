# HybridMaterial

`HybridMaterial` 是 Genesis 引擎中用于混合多种材质特性的材质类，它允许将不同类型的材质（如弹性、塑性、流体等）组合在一起，用于模拟复杂的物理现象。

## 功能说明

`HybridMaterial` 类提供了以下核心功能：

- 多种材质类型的混合和组合
- 可调节的混合权重和参数
- 支持不同物理状态之间的过渡
- 复杂材料特性的模拟
- 与多种求解器兼容

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 材质在材质库中的唯一索引 |
| `uid` | `int` | 材质的全局唯一标识符 |
| `name` | `str` | 材质的名称 |
| `base_material` | `Material` | 基础材质类型 |
| `blend_material` | `Material` | 混合材质类型 |
| `blend_weight` | `float` | 混合权重（0.0-1.0） |
| `density` | `float` | 材质的密度 |
| `friction` | `float` | 材质的摩擦系数 |
| `restitution` | `float` | 材质的弹性恢复系数 |
| `is_built` | `bool` | 材质是否已完全构建 |

## 主要方法

| 方法名 | 参数 | 返回值 | 描述 |
|--------|------|--------|------|
| `build()` | 无 | `None` | 构建混合材质，初始化物理参数 |
| `update()` | 无 | `None` | 更新材质属性 |
| `reset()` | 无 | `None` | 重置材质到初始状态 |
| `set_blend_weight()` | `float` | `None` | 设置混合权重 |
| `set_base_material()` | `Material` | `None` | 设置基础材质 |
| `set_blend_material()` | `Material` | `None` | 设置混合材质 |

## 继承关系

```
MaterialBase
└── HybridMaterial
```

## 使用示例

```python
import genesis as gs

# 创建场景
scene = gs.Scene()

# 创建混合材质
hybrid_material = scene.create_material(
    type='hybrid',
    base_material='elastic',
    blend_material='plastic',
    blend_weight=0.5,
    density=1000.0,
    friction=0.3,
    restitution=0.1
)

# 设置材质属性
hybrid_material.set_blend_weight(0.7)

# 创建使用混合材质的实体
mesh = gs.Mesh.create_sphere(radius=0.5)
entity = scene.add_entity(type='mpm', mesh=mesh, material=hybrid_material)
```

```{eval-rst}
.. autoclass:: genesis.engine.materials.hybrid.HybridMaterial
    :members:
    :show-inheritance:
    :undoc-members:
```
