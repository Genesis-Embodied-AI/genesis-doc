# IMU Sensor

The `IMUSensor` (Inertial Measurement Unit) provides accelerometer, gyroscope, and magnetometer readings for robot state estimation.

## Overview

An IMU sensor measures:

- **Linear acceleration**: 3D acceleration including gravity
- **Angular velocity**: 3D rotational velocity
- **Magnetic field**: 3D magnetic field vector

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="quadruped.urdf"))
base = robot.get_link("base_link")

# Add IMU to robot base
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=base.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
    )
)

scene.build()

# Simulation loop
for i in range(1000):
    scene.step()

    # Get IMU readings (IMUData NamedTuple)
    data = imu.read()
    accel = data.lin_acc  # ([n_envs,] 3) acceleration in m/s^2
    gyro = data.ang_vel   # ([n_envs,] 3) angular velocity in rad/s
    mag = data.mag        # ([n_envs,] 3) magnetic field in Tesla
```

## Configuration

```python
gs.sensors.IMU(
    # Attachment (inherited from RigidSensorOptionsMixin)
    entity_idx=robot.idx,             # Global entity index
    link_idx_local=base.idx_local,    # Local link index
    pos_offset=(0.0, 0.0, 0.0),      # Position offset from link frame
    euler_offset=(0.0, 0.0, 0.0),    # Rotation offset from link frame (degrees)

    # Accelerometer parameters
    acc_noise=(0.01, 0.01, 0.01),              # White noise std per axis (m/s^2)
    acc_random_walk=(0.001, 0.001, 0.001),     # Bias drift std per axis (m/s^3)
    acc_bias=(0.0, 0.0, 0.0),                  # Constant additive bias per axis
    acc_cross_axis_coupling=0.0,               # Cross-axis misalignment
    acc_resolution=0.0,                        # Measurement resolution (0 = no quantization)

    # Gyroscope parameters
    gyro_noise=(0.01, 0.01, 0.01),             # White noise std per axis (rad/s)
    gyro_random_walk=(0.001, 0.001, 0.001),    # Bias drift std per axis (rad/s^2)
    gyro_bias=(0.0, 0.0, 0.0),                # Constant additive bias per axis
    gyro_cross_axis_coupling=0.0,              # Cross-axis misalignment
    gyro_resolution=0.0,                       # Measurement resolution (0 = no quantization)

    # Magnetometer parameters
    mag_noise=(0.0, 0.0, 0.0),                # White noise std per axis
    mag_random_walk=(0.0, 0.0, 0.0),          # Bias drift std per axis
    mag_bias=(0.0, 0.0, 0.0),                 # Constant additive bias per axis
    mag_cross_axis_coupling=0.0,               # Cross-axis misalignment
    mag_resolution=0.0,                        # Measurement resolution (0 = no quantization)

    # Timing
    delay=0.0,                                 # Read delay in seconds
    jitter=0.0,                                # Random delay jitter in seconds
    interpolate=False,                         # Interpolate delayed measurements

    draw_debug=True,
)
```

## Output Format

`read()` and `read_ground_truth()` both return an `IMUData` NamedTuple:

| Field | Type | Shape | Description |
|-------|------|-------|-------------|
| `lin_acc` | `torch.Tensor` (float32) | `([n_envs,] 3)` | Linear acceleration in local sensor frame (m/s^2) |
| `ang_vel` | `torch.Tensor` (float32) | `([n_envs,] 3)` | Angular velocity in local sensor frame (rad/s) |
| `mag` | `torch.Tensor` (float32) | `([n_envs,] 3)` | Magnetic field vector in local sensor frame (Tesla) |

`read()` applies noise, bias, random walk, and cross-axis coupling if configured. `read_ground_truth()` returns noiseless values.

## Noise Modeling

The IMU supports realistic noise modeling based on Allan variance parameters:

### Accelerometer Noise

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `acc_noise` | White noise std | 0.001-0.01 m/s^2 |
| `acc_random_walk` | Bias drift std | 0.0001-0.001 m/s^3 |

### Gyroscope Noise

| Parameter | Description | Typical Value |
|-----------|-------------|---------------|
| `gyro_noise` | White noise std | 0.0001-0.001 rad/s |
| `gyro_random_walk` | Bias drift std | 0.00001-0.0001 rad/s^2 |

## Example: Quadruped State Estimation

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
quadruped = scene.add_entity(gs.morphs.URDF(file="go2.urdf"))
base = quadruped.get_link("base")

# Add IMU with realistic noise
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=quadruped.idx,
        link_idx_local=base.idx_local,
    )
)

scene.build()

# State estimation loop
import torch
velocity_estimate = torch.zeros(3, device=gs.device)
dt = scene.dt

for i in range(1000):
    scene.step()

    data = imu.read()

    # Simple integration (real systems use Kalman filtering)
    velocity_estimate += data.lin_acc * dt
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
