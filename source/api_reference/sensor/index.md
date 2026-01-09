# Sensors

Genesis provides a variety of sensors for perceiving the simulation state. Sensors are attached to entities and provide data such as visual observations, force measurements, and inertial readings.

## Overview

Available sensor types:

| Sensor | Description | Use Case |
|--------|-------------|----------|
| **Camera** | Visual observations (RGB, depth, segmentation) | Vision-based control |
| **ContactForceSensor** | Force/torque at contact points | Manipulation, grasping |
| **IMUSensor** | Accelerometer and gyroscope readings | Robot state estimation |
| **RaycasterSensor** | Ray-based distance measurements | LIDAR, proximity sensing |

## Quick Start

### Adding Sensors

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# Camera sensor (via add_camera)
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

# Build scene first
scene.build()

# Contact force sensor on end-effector
contact_sensor = scene.add_sensor(
    gs.sensors.ContactForce(
        link=robot.get_link("end_effector"),
    )
)

# IMU sensor
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=robot.get_link("base_link"),
    )
)
```

### Reading Sensor Data

```python
scene.step()

# Camera
rgb = cam.render(rgb=True)
depth = cam.render(depth=True)

# Contact force
force = contact_sensor.get_data()

# IMU
imu_data = imu.get_data()
acceleration = imu_data.linear_acceleration
angular_velocity = imu_data.angular_velocity
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
