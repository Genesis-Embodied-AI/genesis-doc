# Viewer

The `Viewer` class provides an interactive window for real-time visualization of simulations. It allows users to navigate the scene with mouse controls, inspect objects, and control simulation playback.

## Overview

The Viewer is an optional component that provides:

- Real-time 3D rendering of the simulation
- Mouse-based camera navigation (orbit, pan, zoom)
- Keyboard shortcuts for controlling simulation
- Entity selection and highlighting
- Render state visualization

## Quick Start

```python
import genesis as gs

gs.init()

# Create scene with interactive viewer
scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3, 0, 2),
        camera_lookat=(0, 0, 0.5),
        res=(1280, 720),
        max_FPS=60,
    ),
)

scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

# Run with viewer
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

## Camera Controls

| Control | Action |
|---------|--------|
| Left Mouse + Drag | Orbit camera |
| Right Mouse + Drag | Pan camera |
| Scroll Wheel | Zoom in/out |
| Middle Mouse + Drag | Zoom |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Pause/Resume simulation |
| R | Reset camera to initial position |
| Esc | Close viewer |

## Configuration

The viewer is configured through `ViewerOptions`:

```python
viewer_options = gs.options.ViewerOptions(
    res=(1920, 1080),          # Resolution
    camera_pos=(5, 0, 3),       # Initial camera position
    camera_lookat=(0, 0, 0),    # Camera look-at point
    camera_fov=45,              # Field of view
    max_FPS=60,                 # Maximum frame rate
    run_in_thread=True,         # Run viewer in separate thread
    enable_interaction=True,    # Enable mouse/keyboard interaction
)
```

## Headless Mode

For environments without a display (servers, CI), disable the viewer:

```python
scene = gs.Scene(show_viewer=False)
```

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.viewer.Viewer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`visualizer` - Main visualization orchestrator
- {doc}`/api_reference/options/options` - ViewerOptions configuration
