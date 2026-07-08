# Camera

The visualization camera renders a scene off-screen to images: color, depth, segmentation, and surface normals. Add one with `scene.add_camera(...)` and read frames with `cam.render(...)`. It renders through the scene's {doc}`renderer <renderers/index>`, needs no display, and works headless. It can move, follow an entity, and record video.

```python
cam = scene.add_camera(
    res=(640, 480),      # (width, height) in pixels
    pos=(3.5, 0.0, 2.5),
    lookat=(0.0, 0.0, 0.5),
    fov=30,
    GUI=False,           # True opens an OpenCV preview window
)
scene.build()

# render() always returns (rgb, depth, segmentation, normal);
# disabled outputs come back as None.
rgb, depth, segmentation, normal = cam.render(
    rgb=True, depth=True, segmentation=True, normal=True
)
```

Each array is shaped `(height, width, ...)`. For image types, video recording, moving and entity-following cameras, and choosing a backend, see {doc}`/user_guide/rendering/rendering`.

:::{note}
Do not confuse this with the {doc}`camera sensor </api_reference/sensor/camera>`. The camera sensor is added with `scene.add_sensor(gs.sensors.*CameraOptions(...))` and its `read()` returns a `CameraReturnType` carrying a single `rgb` field. The visualization camera here renders RGB together with depth, segmentation, and normals.
:::

## API reference

```{eval-rst}
.. autoclass:: genesis.vis.camera.Camera
   :members:
   :undoc-members:
   :show-inheritance:
```

## See also

- {doc}`/user_guide/rendering/rendering`: cameras, image types, and video
- {doc}`renderers/index`: rendering backends
- {doc}`/api_reference/sensor/index`: other sensor types
