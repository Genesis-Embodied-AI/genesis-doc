# Rasterizer

The `Rasterizer` provides fast GPU-accelerated rendering using OpenGL. It's the default renderer for real-time visualization and is suitable for training reinforcement learning agents.

## Overview

The Rasterizer offers:

- **High performance**: 1000+ FPS for simple scenes
- **GPU acceleration**: Leverages OpenGL for rendering
- **Multiple outputs**: RGB, depth, segmentation, normals
- **Multi-environment support**: Efficient batched rendering

## Quick Start

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# Add entities
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="path/to/robot.urdf"))

scene.build()

# Add rasterizer camera (default)
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
)

# Render images
for i in range(100):
    scene.step()

    rgb = cam.render(rgb=True)
    depth = cam.render(depth=True)
    segmentation = cam.render(segmentation=True)
```

## Configuration

The Rasterizer is configured through `RasterizerOptions`:

```python
rasterizer_options = gs.options.RasterizerOptions(
    env_separate_rigid=True,   # Separate rendering per environment
)
```

## Output Types

| Output | Type | Description |
|--------|------|-------------|
| `rgb` | `np.ndarray` (H, W, 3) | RGB color image |
| `depth` | `np.ndarray` (H, W) | Depth values in meters |
| `segmentation` | `np.ndarray` (H, W) | Entity/link segmentation IDs |
| `normal` | `np.ndarray` (H, W, 3) | Surface normals |

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.rasterizer.Rasterizer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`raytracer` - Photorealistic ray tracing renderer
- {doc}`batch_renderer` - High-throughput parallel renderer
- {doc}`/api_reference/options/renderer/rasterizer` - Rasterizer options
