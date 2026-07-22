# Camera sensor

A camera sensor renders an RGB image of the scene each step and returns it through the sensor `read()` interface, so a camera reads like any other sensor: attach it, step, read.

Do not confuse it with the visualization camera. The camera sensor is created with `scene.add_sensor(gs.sensors.*CameraOptions(...))` and its `read()` returns a `CameraReturnType` carrying a single `rgb` field. The visualization camera is created with `scene.add_camera(...)` and its `render()` returns RGB together with depth, segmentation, and surface normals. Reach for the visualization camera when you need those extra channels or the interactive viewer; see {doc}`/api_reference/visualization/camera`.

Each backend is a separate options class and sensor, all returning the same `CameraReturnType(rgb)`. For usage and how to choose a backend, see the {doc}`camera sensing guide </user_guide/sensing/camera_sensors>`.

## Rasterizer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.RasterizerCameraOptions

.. autoclass:: genesis.engine.sensors.camera.RasterizerCameraSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## Raytracer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.RaytracerCameraOptions

.. autoclass:: genesis.engine.sensors.camera.RaytracerCameraSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## Batch renderer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.BatchRendererCameraOptions

.. autoclass:: genesis.engine.sensors.camera.BatchRendererCameraSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: sensor overview and return-shape table.
- {doc}`/api_reference/visualization/camera`: the visualization camera (`scene.add_camera().render()`) for depth, segmentation, and normals.
