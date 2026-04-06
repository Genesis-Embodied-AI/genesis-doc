# Sensors

Genesis provides a variety of sensors for perceiving the simulation state. Sensors are attached to entities and provide data such as visual observations, force measurements, and inertial readings.

## Overview

Available sensor types:

| Sensor | Return Type | Fields | Shape |
|--------|-------------|--------|-------|
| **Camera** | `CameraData` | `rgb` (uint8) | `([n_envs,] h, w, 3)` |
| **ContactSensor** | `torch.Tensor` (bool) | - | `([n_envs,] 1)` |
| **ContactForceSensor** | `torch.Tensor` (float32) | - | `([n_envs,] 3)` |
| **IMUSensor** | `IMUData` | `lin_acc`, `ang_vel`, `mag` (float32) | `([n_envs,] 3)` each |
| **RaycasterSensor** | `RaycasterData` | `points`, `distances` (float32) | `([n_envs,] *shape, 3)`, `([n_envs,] *shape)` |
| **DepthCameraSensor** | `RaycasterData` | `points`, `distances` (float32) | `([n_envs,] h, w, 3)`, `([n_envs,] h, w)` |
| **ProximitySensor** | `torch.Tensor` (float32) | - | `([n_envs,] n_probes)` |
| **KinematicContactProbe** | `KinematicContactProbeData` | `penetration`, `force` (float32) | `([n_envs,] n_probes)`, `([n_envs,] n_probes, 3)` |
| **ElastomerDisplacementSensor** | `torch.Tensor` (float32) | - | `([n_envs,] n_probes, 3)` |
| **TemperatureGridSensor** | `torch.Tensor` (float32) | - | `([n_envs,] nx, ny, nz)` |

## Quick Start

### Adding Sensors

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
end_effector = robot.get_link("end_effector")
base = robot.get_link("base_link")

# Camera sensor (via add_camera)
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

# Contact force sensor on end-effector
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=end_effector.idx_local,
    )
)

# IMU sensor
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=base.idx_local,
    )
)

scene.build()
```

### Reading Sensor Data

```python
scene.step()

# Camera
rgb, _, _, _ = cam.render(rgb=True)
_, depth, _, _ = cam.render(depth=True)

# Contact force
force = contact_sensor.read()

# IMU
imu_data = imu.read()
acceleration = imu_data.lin_acc
angular_velocity = imu_data.ang_vel
```

## Sensor Types

```{toctree}
:titlesonly:

camera
contact
imu
raycaster
```

## See Also

- {doc}`/api_reference/visualization/index` - Visualization system
- {doc}`/api_reference/entity/index` - Adding sensors to entities
