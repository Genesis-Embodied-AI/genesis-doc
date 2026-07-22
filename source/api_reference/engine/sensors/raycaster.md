# Raycaster sensor

`gs.sensors.Raycaster` (also available as `gs.sensors.Lidar`) casts a fixed pattern of rays from a link and returns the hit points and distances, for lidar, proximity, and obstacle sensing. `gs.sensors.DepthCamera` drives the same machinery with a camera ray grid and adds `read_image()`. For usage, how ray casting works, choosing a pattern, and hardware presets, see the {doc}`raycaster sensing guide </user_guide/sensing/raycaster>`.

## `gs.sensors.Raycaster`

Also available as `gs.sensors.Lidar`.

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.Raycaster
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.raycaster.RaycasterReturnType
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.raycaster.RaycasterSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.sensors.DepthCamera`

A raycaster with a `DepthCameraPattern`; `read_image()` reshapes the per-ray distances into a depth image of shape `([n_envs,] height, width)`.

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.DepthCamera
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.depth_camera.DepthCameraSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## Ray patterns

A pattern is a local description of the rays: it fixes a start point and a unit direction per ray in the sensor's frame. Pass an instance as the `pattern` argument, or subclass `RaycastPattern` for a custom layout.

```{eval-rst}
.. autoclass:: genesis.options.sensors.raycaster.RaycastPattern

.. autoclass:: genesis.options.sensors.raycaster.SphericalPattern

.. autoclass:: genesis.options.sensors.raycaster.GridPattern

.. autoclass:: genesis.options.sensors.raycaster.DepthCameraPattern
```

## See also

- {doc}`index`: sensor overview.
- {doc}`/user_guide/sensing/raycaster`: usage, how ray casting works, patterns, and hardware presets.
- {doc}`camera`: visual (RGB) sensing.
