# Visualization and rendering

Genesis World turns a simulation into pixels through two independent paths: an interactive **viewer** window for watching a scene as it runs, and **camera sensors** that render frames you can read back as tensors. This page maps the visualization API and points to the reference for each component.

## Components

- **Visualizer:** the orchestrator behind `scene.visualizer`. It owns the viewer, the camera sensors, and the renderer backend, and it refreshes them when you call `scene.visualizer.update()`.
- **Viewer:** the interactive window for real-time viewing, with mouse and keyboard camera controls. It always uses the rasterizer backend; configure its look through `gs.options.VisOptions` and its initial pose through `gs.options.ViewerOptions`.
- **Camera sensors:** the `Camera` objects added with `scene.add_camera(...)`. They capture RGB, depth, segmentation, and surface-normal images from a chosen viewpoint. Rendering happens through the scene's renderer backend.
- **Renderers:** the backend that camera sensors use to produce images. Choose one per scene with `gs.Scene(renderer=...)`; the choice does not affect the viewer.
- **Lights:** the light sources that illuminate a rendered scene.

## Renderer backends

The renderer is selected once for the whole scene and applies to its camera sensors. Pass an instance of one of the `gs.renderers.*` options classes to `gs.Scene(renderer=...)`:

- **`gs.renderers.Rasterizer`:** the default. Fast, non-photorealistic rendering for real-time viewing, control loops, and reinforcement-learning rollouts.
- **`gs.renderers.RayTracer`:** a path tracer backed by LuisaRender (Luisa), for photorealistic stills. It is being deprecated in favor of Nyx.
- **`gs.renderers.BatchRenderer`:** high-throughput rendering across many environments in parallel on the GPU, for large-scale data collection.

**Nyx** is a separate photorealistic path tracer, distributed as the `gs-nyx` package. Unlike the backends above, it is not a scene-wide renderer: it attaches per camera as a sensor through `scene.add_sensor(...)`, so one scene can pair fast rasterized cameras with a photorealistic Nyx camera. See {doc}`/user_guide/rendering/nyx_renderer` for details.

For usage, see {doc}`/user_guide/interaction/visualization` for the interactive viewer and {doc}`/user_guide/rendering/index` for camera rendering.

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
- {doc}`/api_reference/sensor/camera`: the camera sensor, read through the sensor interface
