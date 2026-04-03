# Cameras

Cameras in Genesis are sensors that capture visual information from the simulation. They can render RGB images, depth maps, segmentation masks, and other visual data.

## Overview

Genesis provides a unified `Camera` class that works with different rendering backends:

- **Rasterizer cameras**: Fast rendering for real-time use
- **Raytracer cameras**: Photorealistic rendering
- **BatchRenderer cameras**: High-throughput parallel rendering

## Adding Cameras

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.build()

# Add a camera
cam = scene.add_camera(
    res=(1280, 720),       # Resolution (width, height)
    pos=(3, 0, 2),         # Camera position
    lookat=(0, 0, 0.5),    # Look-at target
    fov=40,                # Field of view (degrees)
    up=(0, 0, 1),          # Up vector
)
```

## Rendering Images

```python
# Step simulation
scene.step()

# Render different output types
rgb = cam.render(rgb=True)                    # RGB image
depth = cam.render(depth=True)                # Depth map
segmentation = cam.render(segmentation=True)  # Segmentation
normal = cam.render(normal=True)              # Surface normals

# Render multiple types at once
outputs = cam.render(rgb=True, depth=True)
```

## Camera Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `res` | tuple (W, H) | Image resolution |
| `pos` | tuple (x, y, z) | Camera position |
| `lookat` | tuple (x, y, z) | Point camera looks at |
| `up` | tuple (x, y, z) | Up direction |
| `fov` | float | Vertical field of view (degrees) |
| `model` | str | Camera model: `pinhole` or `thinlens` |
| `spp` | int | Samples per pixel (raytracer only) |
| `denoise` | bool | Enable denoising (raytracer only) |

## Camera Models

### Pinhole Camera (Default)

Standard perspective camera with infinite depth of field:

```python
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="pinhole",
)
```

### Thin Lens Camera

Physically-based camera with depth of field:

```python
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="thinlens",
    aperture=0.1,       # Aperture size
    focus_dist=3.0,     # Focus distance
)
```

## Dynamic Camera Control

```python
# Update camera position during simulation
cam.set_pose(
    pos=(5, 0, 3),
    lookat=(0, 0, 0),
)

# Follow an entity
cam.follow_entity(robot, offset=(2, 0, 1))
```

## Components

```{toctree}
:titlesonly:

camera
```

## See Also

- {doc}`/api_reference/visualization/renderers/index` - Rendering backends
- {doc}`/api_reference/sensor/index` - Other sensor types
