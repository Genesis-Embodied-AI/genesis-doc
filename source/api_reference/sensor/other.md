# Other sensors

This page collects the remaining built-in sensors that do not fit the contact, tactile, IMU, camera, or raycaster families: a surface-distance probe, a thermal grid, and a joint-torque sensor.

Create each one from its `gs.sensors.*` options object with `scene.add_sensor()`; the call returns the sensor handle whose `read()` gives the measured value. For the attach-and-read model, batched reads, and configuration with noise, delay, and history, see the {doc}`sensors overview <index>`.

## SurfaceDistanceProbe

Reports the nearest distance from each probe point to the mesh surfaces of a set of tracked rigid links, clamped to `probe_radius` when nothing is in range. The matching nearest points are available on the `nearest_points` attribute. See {doc}`the proximity guide </user_guide/sensing/proximity>`.

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.SurfaceDistanceProbe

.. autoclass:: genesis.engine.sensors.surface_distance_probe.SurfaceDistanceProbeSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## TemperatureGrid

Overlays a 3D voxel grid on one rigid link and reports the temperature of every cell, in degrees Celsius, evolving each cell from contact conduction, radiation, convection, and optional per-cell heat generation. See {doc}`the temperature grid guide </user_guide/sensing/temperature_grid>`.

Material properties are supplied through a `properties_dict` mapping a global rigid-link index to a `TemperatureProperties` entry.

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.TemperatureProperties

.. autoclass:: genesis.options.sensors.options.TemperatureGrid

.. autoclass:: genesis.engine.sensors.temperature.TemperatureGridSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## JointTorque

Measures the generalized effort delivered at each selected actuator's output shaft: torque for revolute dofs, force for prismatic dofs. Because it reads the constraint-solved effort, external contacts show up implicitly as a change in joint load.

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.JointTorque

.. autoclass:: genesis.engine.sensors.joint_torque.JointTorqueSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: Sensor overview
- {doc}`contact`: Contact and contact-force sensing
- {doc}`raycaster`: Ray-based distance measurement
