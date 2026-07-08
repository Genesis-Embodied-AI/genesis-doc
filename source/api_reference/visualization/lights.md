# Lights

Genesis World supports various light sources for illuminating scenes during rendering. Light configuration affects both the interactive viewer and rendered images from cameras.

## Overview

Lighting in Genesis World is configured through visualization options and can include:

- **Directional lights**: Parallel rays simulating distant light sources (sun)
- **Point lights**: Omnidirectional lights at specific positions
- **Ambient lighting**: Global illumination level

## Configuration

Lighting is configured through `VisOptions`. Each entry in `lights` is a dict matching one of the light option classes, selected by its `type` field:

- `"directional"`: requires `dir`, `color`, and `intensity`.
- `"point"`: requires `pos`, `color`, and `intensity`.
- `"ambient"`: requires `color` and `intensity`.

`color` is an RGB triple with each channel in `[0, 1]`, and it is required for every light. `dir` is the direction the light travels along (not a position).

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    vis_options=gs.options.VisOptions(
        ambient_light=(0.3, 0.3, 0.3),  # RGB ambient light, each channel in [0, 1]
        lights=[
            {"type": "directional", "dir": (1, 1, -1), "color": (1.0, 1.0, 1.0), "intensity": 5.0},
        ],
    ),
)
```

## Raytracer lighting

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

## See also

- {doc}`/api_reference/options/options` - VisOptions configuration
- {doc}`renderers/raytracer` - Raytracer for photorealistic rendering
- {doc}`/api_reference/options/surface/emission/index` - Emissive surfaces
