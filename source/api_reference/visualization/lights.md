# 灯光（Lights）

Genesis 支持各种光源来照亮渲染场景。灯光配置会影响交互式 viewer 和相机渲染的图像。

## 概述

Genesis 中的灯光通过可视化选项进行配置，可以包括：

- **方向光（Directional lights）**：平行光线，模拟远处光源（如太阳）
- **点光源（Point lights）**：特定位置的全向光源
- **环境光（Ambient lighting）**：全局照明水平

## 配置

通过 `VisOptions` 配置灯光：

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    vis_options=gs.options.VisOptions(
        ambient_light=(0.3, 0.3, 0.3),  # RGB 环境光
        lights=[
            {"type": "directional", "direction": (1, 1, -1), "intensity": 1.0},
        ],
    ),
)
```

## Raytracer 灯光

使用 raytracer 渲染器时，额外的灯光选项可用于照片级真实感渲染：

- 用于基于图像照明的环境贴图
- 用于柔和阴影的面积光
- 自发光材质

```python
# 添加使用 raytracer 的相机
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    renderer="raytracer",
)
```

## 另请参阅

- {doc}`/api_reference/options/options` - VisOptions 配置
- {doc}`renderers/raytracer` - 用于照片级真实感渲染的 Raytracer
- {doc}`/api_reference/options/surface/emission/index` - 自发光表面
