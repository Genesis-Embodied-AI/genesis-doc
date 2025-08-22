# 🖲️ Sensors

Robots need sensors to observe the world around them.
In Genesis, sensors extract information from the scene, computing values using the state of the scene but not affecting the scene itself.
All sensors have a `read()` method that returns the measured sensor data and `read_ground_truth()` which returns the ground truth data.

Currently only IMU and rigid tactile sensors are supported, but soft tactile and distance (LiDAR) sensors are coming soon!

## IMU Example

In this tutorial, we'll walk through how to set up an Inertial Measurement Unit (IMU) sensor on a robotic arm's end-effector. The IMU will measure linear acceleration and angular velocity as the robot traces a circular path, and we'll visualize the data in real-time with realistic noise parameters.

The full example script is available at `examples/sensors/imu.py`.

### Scene Setup

First, let's create our simulation scene and load the robotic arm:

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    sim_options=gs.options.SimOptions(
        dt=0.01,
    ),
    show_viewer=True,
)

########################## entities ##########################
scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
end_effector = franka.get_link("hand")
motors_dof = np.arange(7)
```

Here we set up a basic scene with a Franka robotic arm. The camera is positioned to give us a good view of the robot's workspace, and we identify the end-effector link where we'll attach our IMU sensor.

### Adding the IMU Sensor

We "attach" the IMU sensor onto the entity at the end effector by specifying the `entity_idx` and `link_idx_local`.

```python
imu = scene.add_sensor(
    gs.sensors.IMUOptions(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        # sensor characteristics
        acc_axes_skew=(0.0, 0.01, 0.02),
        gyro_axes_skew=(0.03, 0.04, 0.05),
        acc_noise_std=(0.01, 0.01, 0.01),
        gyro_noise_std=(0.01, 0.01, 0.01),
        acc_bias_drift_std=(0.001, 0.001, 0.001),
        gyro_bias_drift_std=(0.001, 0.001, 0.001),
        delay=0.01,
        jitter=0.01,
        interpolate_for_delay=True,
    )
)
```

The `IMUOptions` also has options to configure the following sensor characteristics:
- `acc_axes_skew` and `gyro_axes_skew` simulate sensor misalignment
- `acc_noise_std` and `gyro_noise_std` add Gaussian noise to measurements
- `acc_bias_drift_std` and `gyro_bias_drift_std` simulate gradual sensor drift over time
- `delay` and `jitter` introduce timing realism
- `interpolate_for_delay` smooths delayed measurements

### Motion Control and Simulation

Now let's build the scene and create circular motion to generate interesting IMU readings:

```python
########################## build and control ##########################
scene.build()

franka.set_dofs_kp(np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]))
franka.set_dofs_kv(np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]))

# Create a circular path for end effector to follow
circle_center = np.array([0.4, 0.0, 0.5])
circle_radius = 0.15
rate = 2 / 180 * np.pi  # Angular velocity in radians per step

def control_franka_circle_path(i):
    pos = circle_center + np.array([np.cos(i * rate), np.sin(i * rate), 0]) * circle_radius
    qpos = franka.inverse_kinematics(
        link=end_effector,
        pos=pos,
        quat=np.array([0, 1, 0, 0]),  # Keep orientation fixed
    )
    franka.control_dofs_position(qpos[:-2], motors_dof)
    scene.draw_debug_sphere(pos, radius=0.01, color=(1.0, 0.0, 0.0, 0.5))  # Visualize target

# Run simulation
for i in range(1000):
    scene.step()
    control_franka_circle_path(i)
```

The robot traces a horizontal circle while maintaining a fixed orientation. The circular motion creates centripetal acceleration that the IMU will detect, along with any gravitational effects based on the sensor's orientation.

After building the scene, you can access both measured and ground truth IMU data:

```python
# Access sensor readings
print("Ground truth data:")
print(imu.read_ground_truth())
print("Measured data:")
print(imu.read())
```

The IMU returns data in a dictionary format with keys:
- `"lin_acc"`: Linear acceleration in m/s² (3D vector)
- `"ang_vel"`: Angular velocity in rad/s (3D vector)

### Data Recording

We can add "recorders" to any sensor to automatically read and process data without slowing down the simulation. This can be used to stream or save formatted data to a file, or visualize the data live!

#### Real-time Data Visualization

Using `PyQtGraphPlotter`, we can visualize the sensor data while the simulation is running.
Make sure to install [PyQtGraph](https://www.pyqtgraph.org) (`pip install pyqtgraph`)!

```python
from genesis.sensors.data_handlers import PyQtGraphPlotter

...
# before scene.build()

imu.add_recorder(
    handler=PyQtGraphPlotter(title="IMU Accelerometer Measured Data", labels=["acc_x", "acc_y", "acc_z"]),
    rec_options=gs.options.RecordingOptions(
        preprocess_func=lambda data, ground_truth_data: data["lin_acc"],
    ),
)
imu.add_recorder(
    handler=PyQtGraphPlotter(title="IMU Accelerometer Ground Truth Data", labels=["acc_x", "acc_y", "acc_z"]),
    rec_options=gs.options.RecordingOptions(
        preprocess_func=lambda data, ground_truth_data: ground_truth_data["lin_acc"],
    ),
)
imu.start_recording()
```

This sets up two live plots: one showing the noisy measured accelerometer data and another showing the ground truth values. The `preprocess_func` extracts just the linear acceleration data from the full IMU readings which contain both accelerometer and gyroscope data.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>