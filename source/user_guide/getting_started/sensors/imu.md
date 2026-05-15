# 🧭 IMU

The `IMU` sensor models an Inertial Measurement Unit attached to a rigid link. It returns linear acceleration, angular velocity, and magnetic field as a `NamedTuple` (`lin_acc`, `ang_vel`, `mag`), with optional misalignment, noise, drift, delay, and jitter to mimic real hardware.

The full example script is at `examples/sensors/imu_franka.py`.

## Scene setup

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    sim_options=gs.options.SimOptions(dt=0.01),
    show_viewer=True,
)

scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))
end_effector = franka.get_link("hand")
motors_dof = (0, 1, 2, 3, 4, 5, 6)
```

## Adding the IMU sensor

Attach the IMU onto the entity at the end effector by specifying `entity_idx` and `link_idx_local`:

```python
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
        # sensor characteristics
        acc_cross_axis_coupling=(0.0, 0.01, 0.02),
        gyro_cross_axis_coupling=(0.03, 0.04, 0.05),
        acc_noise=(0.01, 0.01, 0.01),
        gyro_noise=(0.01, 0.01, 0.01),
        acc_random_walk=(0.001, 0.001, 0.001),
        gyro_random_walk=(0.001, 0.001, 0.001),
        delay=0.01,
        jitter=0.01,
        interpolate=True,
        draw_debug=True,
    )
)
```

The IMU constructor exposes:

- `pos_offset` - sensor position relative to the link frame.
- `acc_cross_axis_coupling` / `gyro_cross_axis_coupling` - sensor misalignment.
- `acc_noise` / `gyro_noise` - Gaussian noise per axis.
- `acc_random_walk` / `gyro_random_walk` - gradual drift over time.
- `delay` / `jitter` - timing realism.
- `interpolate` - smooth delayed measurements between ring slots.
- `draw_debug` - visualize the sensor frame in the viewer.

## Motion control and simulation

```python
scene.build()

franka.set_dofs_kp(np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]))
franka.set_dofs_kv(np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]))

circle_center = np.array([0.4, 0.0, 0.5])
circle_radius = 0.15
rate = np.deg2rad(2.0)

def control_franka_circle_path(i):
    pos = circle_center + np.array([np.cos(i * rate), np.sin(i * rate), 0]) * circle_radius
    qpos = franka.inverse_kinematics(
        link=end_effector,
        pos=pos,
        quat=np.array([0, 1, 0, 0]),
    )
    franka.control_dofs_position(qpos[:-2], motors_dof)
    scene.draw_debug_sphere(pos, radius=0.01, color=(1.0, 0.0, 0.0, 0.5))

for i in range(1000):
    scene.step()
    control_franka_circle_path(i)
```

The robot traces a horizontal circle while maintaining a fixed orientation. The circular motion creates centripetal acceleration that the IMU detects, along with gravitational effects based on the sensor's orientation.

After the build, both measured and ground truth IMU data are available:

```python
print("Ground truth data:")
print(imu.read_ground_truth())
print("Measured data:")
print(imu.read())
```

The IMU returns data as a `NamedTuple` with fields:

- `lin_acc` - linear acceleration in m/s² (3D vector)
- `ang_vel` - angular velocity in rad/s (3D vector)
- `mag` - magnetic field in Tesla (3D vector)

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>
