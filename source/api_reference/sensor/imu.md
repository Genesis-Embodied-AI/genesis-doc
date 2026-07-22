# IMU sensor

`gs.sensors.IMU` reports accelerometer, gyroscope, and magnetometer readings from a link, for robot state estimation. For usage, the noise model, and a worked state-estimation loop, see the {doc}`IMU sensing guide </user_guide/sensing/imu>`.

## API reference

```{eval-rst}
.. autoclass:: genesis.options.sensors.options.IMU
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.imu.IMUReturnType
```

```{eval-rst}
.. autoclass:: genesis.engine.sensors.imu.IMUSensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: sensor overview.
- {doc}`/user_guide/sensing/imu`: IMU usage, noise modeling, and state estimation.
- {doc}`contact`: contact and force sensing.
