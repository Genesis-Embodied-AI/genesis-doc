# Lights

Genesis supports various light sources for illuminating scenes during rendering. Light configuration affects both the interactive viewer and rendered images from cameras.

## Overview

Lighting in Genesis is configured through visualization options and can include:

- **Directional lights**: Parallel rays simulating distant light sources (sun)
- **Point lights**: Omnidirectional lights at specific positions
- **Ambient lighting**: Global illumination level

## Configuration

Lighting is configured through `VisOptions`:

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    vis_options=gs.options.VisOptions(
        ambient_light=(0.3, 0.3, 0.3),  # RGB ambient light
        lights=[
            {"type": "directional", "direction": (1, 1, -1), "intensity": 1.0},
        ],
    ),
)
```

## Raytracer Lighting

When using the raytracer renderer, additional lighting options are available for photorealistic rendering:

- Environment maps for image-based lighting
- Area lights for soft shadows
- Emissive materials

```python
# Add camera with raytracer
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    renderer="raytracer",
)
```

## See Also

- {doc}`/api_reference/options/options` - VisOptions configuration
- {doc}`renderers/raytracer` - Raytracer for photorealistic rendering
- {doc}`/api_reference/options/surface/emission/index` - Emissive surfaces
