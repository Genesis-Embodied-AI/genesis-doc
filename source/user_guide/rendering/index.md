# Rendering

Choose how to view the scene or read images from it before choosing a renderer. The interactive viewer, visualization cameras, and camera sensors serve different purposes and use different interfaces:

| Task | Interface | Guide |
|---|---|---|
| Inspect and interact with a running scene | `gs.Scene(show_viewer=True)` | {doc}`Viewer </user_guide/interaction/visualization>` |
| Render RGB, depth, segmentation, or normals on demand, or record video | `scene.add_camera(...)`, then `render()` or `start_recording()` | {doc}`Cameras <cameras>` |
| Read RGB images through the sensor pipeline, for example from a robot-mounted camera | `scene.add_sensor(...)`, then `read()` | {doc}`Camera sensors </user_guide/sensing/camera_sensors>` |
| Render photorealistic images through a Nyx camera sensor | `scene.add_sensor(NyxCameraOptions(...))`, then `read()` | {doc}`Nyx renderer <nyx_renderer>` |

Visualization cameras use the renderer selected on the scene; the {doc}`camera guide <cameras>` covers the rasterizer, batch renderer, and legacy Luisa ray tracer. Nyx attaches as a camera sensor with its own renderer. The available image channels and recording workflow depend on the interface.

{doc}`Surfaces and textures <surfaces_textures>` explains how to configure materials and appearance for rendering.

```{toctree}
:hidden:
:maxdepth: 1

cameras
surfaces_textures
nyx_renderer
```
