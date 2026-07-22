# Visualization and rendering

Genesis World turns a simulation into pixels through two independent paths: an interactive **viewer** window for watching a scene as it runs, and **camera sensors** that render frames you can read back as tensors. This page maps the visualization API and points to the reference for each component.

## Components

- **Visualizer:** the orchestrator behind `scene.visualizer`. It owns the viewer, the camera sensors, and the renderer backend, and it refreshes them when you call `scene.visualizer.update()`.
- **Viewer:** the interactive window for real-time viewing, with mouse and keyboard camera controls. It always uses the rasterizer backend; configure its look through `gs.options.VisOptions` and its initial pose through `gs.options.ViewerOptions`.
- **Camera sensors:** the `Camera` objects added with `scene.add_camera(...)`. They capture RGB, depth, segmentation, and surface-normal images from a chosen viewpoint. Rendering happens through the scene's renderer backend.
- **Renderers:** the backend that camera sensors use to produce images. Choose one per scene with `gs.Scene(renderer=...)`; the choice does not affect the viewer.
- **Lights:** the light sources that illuminate a rendered scene.

For the interactive viewer see {doc}`/user_guide/interaction/visualization`, and for camera rendering and choosing a backend see {doc}`/user_guide/rendering/index`.

## Reference

```{toctree}
:titlesonly:

visualizer
viewer
camera
renderers/index
lights
```

## See also

- {doc}`/user_guide/interaction/visualization`: the interactive viewer and command-line tools
- {doc}`/user_guide/rendering/index`: cameras, image types, video, and rendering backends
- {doc}`/api_reference/engine/sensors/camera`: the camera sensor, read through the sensor interface
