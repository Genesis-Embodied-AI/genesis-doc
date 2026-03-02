# Renderers

Genesis provides multiple rendering backends optimized for different use cases. Each renderer offers different trade-offs between speed and visual quality.

## Available Renderers

| Renderer | Speed | Quality | Use Case |
|----------|-------|---------|----------|
| **Rasterizer** | Fast | Good | Real-time visualization, RL training |
| **Raytracer** | Slow | Photorealistic | High-quality images, videos |
| **BatchRenderer** | Very Fast | Good | Parallel rendering for large-scale RL |

## Choosing a Renderer

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.build()

# Rasterizer (default, fast)
cam_raster = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0),
)

# Raytracer (photorealistic)
cam_raytrace = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0),
    spp=256,  # Samples per pixel
)
```

## Renderer Components

```{toctree}
:titlesonly:

rasterizer
raytracer
batch_renderer
```

## See Also

- {doc}`/api_reference/options/renderer/index` - Renderer configuration options
