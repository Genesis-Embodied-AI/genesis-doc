# IMU sensor

`gs.sensors.IMU` reports accelerometer, gyroscope, and magnetometer readings from a link, for robot state estimation. For the noise model, configuration guidance, and a worked state-estimation loop, see the {doc}`IMU sensing guide </user_guide/sensing/imu>`.

## Minimal example

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=0,          # the base link
        pos_offset=(0.0, 0.0, 0.1),
    )
)
scene.build()
scene.step()

data = imu.read()      # IMUReturnType, readings in the sensor-local frame
accel = data.lin_acc   # shape ([n_envs,] 3), m/s^2
gyro = data.ang_vel    # shape ([n_envs,] 3), rad/s
mag = data.mag         # shape ([n_envs,] 3), tesla
```

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
- {doc}`/user_guide/sensing/imu`: IMU noise modeling and state estimation.
- {doc}`contact`: contact and force sensing.
