# Camera

The `Camera` class is the primary interface for visual sensing in Genesis. It provides a unified API for rendering images using different backends.

## Overview

A Camera can capture:

- **RGB images**: Color renderings of the scene
- **Depth maps**: Distance from camera to surfaces
- **Segmentation**: Per-pixel entity/link identification
- **Normals**: Surface normal vectors

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.camera.Camera
   :members:
   :undoc-members:
   :show-inheritance:
```

## Examples

### Basic Rendering

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

scene.step()
rgb = cam.render(rgb=True)
print(rgb.shape)  # (480, 640, 3)
```

### Saving Images

```python
import cv2

rgb = cam.render(rgb=True)
cv2.imwrite("output.png", rgb[..., ::-1])  # RGB to BGR for OpenCV
```

### Depth Visualization

```python
import numpy as np

depth = cam.render(depth=True)

# Normalize for visualization
depth_vis = (depth - depth.min()) / (depth.max() - depth.min())
depth_vis = (depth_vis * 255).astype(np.uint8)
```

### With GUI Display

```python
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    GUI=True,  # Show in separate window
)
```

## See Also

- {doc}`index` - Camera overview and parameters
- {doc}`/api_reference/visualization/renderers/index` - Renderer backends
