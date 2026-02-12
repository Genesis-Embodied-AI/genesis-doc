# 渲染器（Renderers）

Genesis 提供了多种针对不同使用场景优化的渲染后端。每个渲染器在速度和视觉质量之间提供不同的权衡。

## 可用渲染器

| 渲染器 | 速度 | 质量 | 使用场景 |
|----------|-------|---------|----------|
| **Rasterizer** | 快 | 良好 | 实时可视化、RL 训练 |
| **Raytracer** | 慢 | 照片级真实感 | 高质量图像、视频 |
| **BatchRenderer** | 非常快 | 良好 | 大规模 RL 的并行渲染 |

## 选择渲染器

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.build()

# Rasterizer（默认，快速）
cam_raster = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0),
)

# Raytracer（照片级真实感）
cam_raytrace = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0),
    spp=256,  # 每像素采样数
)
```

## 渲染器组件

```{toctree}
:titlesonly:

rasterizer
raytracer
batch_renderer
```

## 另请参阅

- {doc}`/api_reference/options/renderer/index` - 渲染器配置选项
