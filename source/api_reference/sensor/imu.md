# IMU Sensor

The `IMUSensor` (Inertial Measurement Unit) provides accelerometer and gyroscope readings for robot state estimation.

## Overview

An IMU sensor measures:

- **Linear acceleration**: 3D acceleration including gravity
- **Angular velocity**: 3D rotational velocity
- **Orientation**: Current orientation (optional)

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="quadruped.urdf"))
scene.build()

# Add IMU to robot base
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=robot.get_link("base_link"),
    )
)

# Simulation loop
for i in range(1000):
    scene.step()

    # Get IMU readings
    data = imu.get_data()
    accel = data.linear_acceleration  # (3,) acceleration in m/s^2
    gyro = data.angular_velocity      # (3,) angular velocity in rad/s
```

## Configuration

```python
gs.sensors.IMU(
    link=link,                    # RigidLink to attach sensor to
    frame="local",                # Reference frame: "world" or "local"

    # Accelerometer parameters
    accel_noise_density=0.0,      # Noise density (m/s^2/sqrt(Hz))
    accel_random_walk=0.0,        # Random walk (m/s^3/sqrt(Hz))
    accel_bias_correlation_time=0.0,  # Bias correlation time (s)

    # Gyroscope parameters
    gyro_noise_density=0.0,       # Noise density (rad/s/sqrt(Hz))
    gyro_random_walk=0.0,         # Random walk (rad/s^2/sqrt(Hz))
    gyro_bias_correlation_time=0.0,   # Bias correlation time (s)
)
```

## Noise Modeling

The IMU supports realistic noise modeling based on Allan variance parameters:

### Accelerometer Noise

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `accel_noise_density` | White noise | 0.001-0.01 m/s^2/sqrt(Hz) |
| `accel_random_walk` | Bias instability | 0.0001-0.001 m/s^3/sqrt(Hz) |

### Gyroscope Noise

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `gyro_noise_density` | White noise | 0.0001-0.001 rad/s/sqrt(Hz) |
| `gyro_random_walk` | Bias instability | 0.00001-0.0001 rad/s^2/sqrt(Hz) |

## Example: Quadruped State Estimation

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
quadruped = scene.add_entity(gs.morphs.URDF(file="go2.urdf"))
scene.build()

# Add IMU with realistic noise
imu = scene.add_sensor(
    gs.sensors.IMU(
        link=quadruped.get_link("base"),
    )
)

# State estimation loop
velocity_estimate = np.zeros(3)
dt = scene.dt

for i in range(1000):
    scene.step()

    data = imu.get_data()

    # Simple integration (real systems use Kalman filtering)
    velocity_estimate += data.linear_acceleration * dt
```

## API Reference

```{eval-rst}
.. autoclass:: genesis.engine.sensors.IMUSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Sensor overview
- {doc}`contact` - Contact force sensing
