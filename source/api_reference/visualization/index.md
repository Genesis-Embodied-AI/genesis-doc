# Visualization & Rendering

Genesis provides a comprehensive visualization system for rendering simulations. The system supports multiple rendering backends including fast rasterization for real-time viewing and ray tracing for photorealistic output.

## Overview

The visualization system is built around three main components:

- **Visualizer**: The main orchestrator that manages cameras, viewers, and renderers
- **Viewer**: Interactive window for real-time visualization with camera controls
- **Renderers**: Backend-specific rendering engines (Rasterizer, Raytracer, BatchRenderer)

## Quick Start

```python
import genesis as gs

gs.init()

# Create a scene with visualization
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3, 0, 2),
        camera_lookat=(0, 0, 0.5),
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
    ),
)

# Add entities and build
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

# Interactive viewing
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

## Components

```{toctree}
:titlesonly:

visualizer
viewer
renderers/index
cameras/index
lights
```

## See Also

- {doc}`/api_reference/options/renderer/index` - Renderer configuration options
- {doc}`/api_reference/options/options` - Viewer and visualization options
