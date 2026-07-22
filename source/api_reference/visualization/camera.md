# Camera

The visualization camera renders a scene off-screen to images: color, depth, segmentation, and surface normals. Add one with `scene.add_camera(...)` and read frames with `cam.render(...)`. It renders through the scene's {doc}`renderer <renderers/index>`, needs no display, and works headless. It can move, follow an entity, and record video. `cam.render(...)` always returns a `(rgb, depth, segmentation, normal)` tuple, with disabled outputs returned as `None`; each array is shaped `(height, width, ...)`. For image types, video recording, moving and entity-following cameras, and choosing a backend, see {doc}`/user_guide/rendering/index`.

:::{note}
Do not confuse this with the {doc}`camera sensor </api_reference/engine/sensors/camera>`. The camera sensor is added with `scene.add_sensor(gs.sensors.*CameraOptions(...))` and its `read()` returns a `CameraReturnType` carrying a single `rgb` field. The visualization camera here renders RGB together with depth, segmentation, and normals.
:::

## API reference

```{eval-rst}
.. autoclass:: genesis.vis.camera.Camera
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/rendering/index`: cameras, image types, and video
- {doc}`renderers/index`: rendering backends
- {doc}`/api_reference/engine/sensors/index`: other sensor types
