# Visualizer

The `Visualizer` class is the main orchestrator for all visualization and rendering in Genesis. It manages the viewer, cameras, and renderer backends.

## Overview

The Visualizer is automatically created when you create a `Scene` and is responsible for:

- Managing the interactive `Viewer` window
- Coordinating multiple `Camera` instances
- Handling renderer backends (Rasterizer, Raytracer, BatchRenderer)
- Synchronizing render state with simulation

## Access

The Visualizer is accessed through the scene:

```python
import genesis as gs

gs.init()
scene = gs.Scene(show_viewer=True)
scene.build()

# Access the visualizer
visualizer = scene.visualizer

# Update the visualization
visualizer.update()
```

## Common Operations

### Adding Cameras

```python
# Add a camera for rendering
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
)
```

### Updating the View

```python
# Update visualization each step
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

### Controlling the Viewer

```python
# Access the interactive viewer
viewer = scene.visualizer.viewer

# Check if viewer is active
if scene.visualizer.viewer is not None:
    # Viewer operations available
    pass
```

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.Visualizer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`viewer` - Interactive viewer for real-time visualization
- {doc}`renderers/index` - Renderer backends
- {doc}`cameras/index` - Camera sensors
