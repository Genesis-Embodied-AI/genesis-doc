# 🖲️ Sensors

Robots need sensors to observe the world around them.
In Genesis, sensors extract information from the scene, computing values using the state of the scene but not affecting the scene itself.

Sensors can be created with `scene.add_sensor(sensor_options)` and read with `sensor.read()` or `sensor.read_ground_truth()`.
```python
scene = ...

# 1. Add sensors to the scene
sensor = scene.add_sensor(
    gs.sensors.Contact(
        ...,
        draw_debug=True, # visualize the sensor data in the scene viewer
    )
)

# 2. Build the scene
scene.build()

for _ in range(1000):
    scene.step()

    # 3. Read data from sensors
    measured_data = sensor.read()
    ground_truth_data = sensor.read_ground_truth()
```

Currently supported sensors:
- `IMU` (accelerometer and gyroscope)
- `Contact` (boolean per rigid link)
- `ContactForce` (xyz force per rigid link)
- `KinematicContactProbe` (penetration-based tactile probes)
- `ElastomerDisplacement` (soft tactile displacement field)
- `Proximity` (distance to tracked mesh surfaces)
- `TemperatureGrid` (voxelized temperature field on a rigid link)
- `Raycaster`
  - `Lidar`
  - `DepthCamera`
<!-- - `RGBCamera` -->

Example usage of sensors can be found under `examples/sensors/`.


## IMU Example

In this tutorial, we'll walk through how to set up an Inertial Measurement Unit (IMU) sensor on a robotic arm's end-effector. The IMU will measure linear acceleration and angular velocity as the robot traces a circular path, and we'll visualize the data in real-time with realistic noise parameters.

The full example script is available at `examples/sensors/imu_franka.py`.

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
motors_dof = (0, 1, 2, 3, 4, 5, 6)
```

Here we set up a basic scene with a Franka robotic arm. The camera is positioned to give us a good view of the robot's workspace, and we identify the end-effector link where we'll attach our IMU sensor.

### Adding the IMU Sensor

We "attach" the IMU sensor onto the entity at the end effector by specifying the `entity_idx` and `link_idx_local`.

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

The `gs.sensors.IMU` constructor has options to configure the following sensor characteristics:
- `pos_offset` specifies the sensor's position relative to the link frame
- `acc_cross_axis_coupling` and `gyro_cross_axis_coupling` simulate sensor misalignment
- `acc_noise` and `gyro_noise` add Gaussian noise to measurements
- `acc_random_walk` and `gyro_random_walk` simulate gradual sensor drift over time
- `delay` and `jitter` introduce timing realism
- `interpolate` smooths delayed measurements
- `draw_debug` visualizes the sensor frame in the viewer

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
rate = np.deg2rad(2.0)  # Angular velocity in radians per step

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

The IMU returns data as a **named tuple** with fields:
- `lin_acc`: Linear acceleration in m/s² (3D vector)
- `ang_vel`: Angular velocity in rad/s (3D vector)

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>

## Tactile Sensors

### Contact Sensors

The contact sensors retrieve contact information per rigid link from the rigid solver.
`Contact` sensor will return a boolean, and `ContactForce` returns the net force vector in the local frame of the associated rigid link.
<!-- NOTE: Untested with other solver couplings -->

The full example script is available at `examples/sensors/contact_force_go2.py` (add flag `--force` to use force sensor).

```{figure} ../../_static/images/contact_force_sensor.png
```

### KinematicContactProbe Sensor
 The `KinematicContactProbe` is a tactile sensor that samples contact depth at user-defined probe positions attached to a rigid link. Instead of returning solver contact forces, it computes a simple penetration-based force estimate per probe: a 3D vector whose magnitude is `stiffness * penetration` and whose direction is given by the probe normal, i.e. `force = stiffness * penetration * normal`.
```python
probe = scene.add_sensor(
    gs.sensors.KinematicContactProbe(
        entity_idx=platform.idx,
        link_idx_local=0,
        probe_local_pos=probe_positions,
        probe_local_normal=probe_normals,
        probe_radius=probe_radii,
        stiffness=5000.0,
        draw_debug=True,
    )
)

scene.build()

data = probe.read()
print(data.penetration)  # shape ([n_envs,] n_probes)
print(data.force)        # shape ([n_envs,] n_probes, 3)
```

The full interactive example is available at `examples/sensors/kinematic_contact_probe.py`.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/kin_probe_data.mp4" type="video/mp4">
</video>

Because the probes are defined in the link-local frame, a regular grid can be used to imitate taxels on a tactile surface.

### ElastomerDisplacement Sensor
The `ElastomerDisplacement` sensor models a soft tactile skin without the computational expense of actually simulating deformation. Each probe reports a 3D displacement vector caused by local indentation, shear, and twist.

You can tune the response of the sensor with coefficients which determine the spatial effect (which is computed with `exp(-coeff * dist^2)`, so larger values make effects more local and smaller values spread them farther):
- `dilate_coefficient`: spread of normal indentation.
- `shear_coefficient`: spread of tangential slip.
- `twist_coefficient`: spread of torsional displacement.

```python
tactile = scene.add_sensor(
    gs.sensors.ElastomerDisplacement(
        entity_idx=pusher.idx,
        link_idx_local=0,
        probe_local_pos=gu.generate_grid_points_on_plane(
            lo=[-0.05, -0.05, -0.025],
            hi=[0.05, 0.05, -0.025],
            normal=(0.0, 0.0, -1.0),
            nx=6,
            ny=8,
        ),
        probe_local_normal=(0.0, 0.0, -1.0),
        probe_radius=0.01,
        dilate_coefficient=1e1,
        shear_coefficient=1e-2,
        twist_coefficient=1e-2,
        draw_debug=True,
    )
)

scene.build()

displacement = tactile.read()
print(displacement)  # shape ([n_envs,] n_probes, 3)
```

When `probe_local_pos` is provided as a 2D grid, Genesis uses an FFT-based algorithm to accelerate the computation for larger tactile arrays.

Example script `examples/sensors/tactile_elastomer_sandbox.py` demos a spherical or box shaped pusher interacting with other objects.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/elastomer_sandbox.mp4" type="video/mp4">
</video>

Another example script `examples/sensors/tactile_elastomer_franka.py` sensorizes the robot arm's gripper fingers with taxels arranged in a grid.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/elastomer_franka.mp4" type="video/mp4">
</video>


## Raycaster Sensors: Lidar and Depth Camera

The `Raycaster` sensor measures distance by casting rays into the scene and detecting intersections with geometry.
The number of rays and ray directions can be specified with a `RaycastPattern`.
`SphericalPattern` supports Lidar-like specification of field of view and angular resolution, and `GridPattern` casts rays from a plane. `DepthCamera` sensors provide the `read_image()` function which formats the raycast information as a depth image. See the API reference for details on the available options.

```python
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.Spherical(),
        entity_idx=robot.idx, # attach to a rigid entity
        pos_offset=(0.3, 0.0, 0.1) # offset from attached entity
        return_world_frame=True, # whether to return points in world frame or local frame
    )
)

depth_camera = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=gs.sensors.DepthCameraPattern(
            res=(480, 360), # image resolution in width, height
            fov_horizontal=90, # field of view in degrees
            fov_vertical=40,
        ),
    )
)

...

lidar.read() # returns a NamedTuple containing points and distances
depth_camera.read_image() # returns tensor of distances as shape (height, width)

```

An example script which demonstrates a raycaster sensor mounted on a robot is available at `examples/sensors/lidar_teleop.py`.
Set the flag `--pattern` to `spherical` for a Lidar like pattern, `grid` for planar grid pattern, and `depth` for depth camera.

Here's what running `python examples/sensors/lidar_teleop.py --pattern depth` looks like:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/depth_camera.mp4" type="video/mp4">
</video>

## Proximity Sensor

The `Proximity` sensor reports the nearest distance from one or more local probe positions to a selected set of tracked rigid links. Each probe returns the nearest point on any tracked mesh surface within `max_range`.

```python
sensor = scene.add_sensor(
    gs.sensors.Proximity(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("palm").idx_local,
        probe_local_pos=((0.0, 0.0, 0.0),),
        track_link_idx=(duck.base_link_idx, box.base_link_idx),  # global rigid link idx
        max_range=0.5,
        draw_debug=True,
    )
)

scene.build()

data = sensor.read()
print(data.distance)  # shape ([n_envs,] n_probes)
print(data.points)    # shape ([n_envs,] n_probes, 3)
```

If no tracked mesh is found within `max_range`, the reported distance is clamped to `max_range` and the returned points are the probe positions.

The interactive example at `examples/sensors/proximity_shadowhand.py` mounts proximity probes on the palm and fingertips of a dexterous robot hand.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/proximity.mp4" type="video/mp4">
</video>


## TemperatureGrid Sensor

The `TemperatureGrid` sensor discretizes the bounding box of a rigid link into a 3D voxel grid and returns the temperature of each cell in Celsius. Heat transfer is driven by contact, conduction, radiation, convection, and optional per-cell heat generation.

To use it, provide a `properties_dict` describing the thermal material properties of the links that may participate in heat exchange. Key `-1` can be used as a default entry for links that are not listed explicitly.

```python
temperature_sensor = scene.add_sensor(
    gs.sensors.TemperatureGrid(
        entity_idx=entity.idx,
        link_idx_local=0,
        grid_size=(10, 10, 1),
        properties_dict={
            -1: gs.sensors.TemperatureProperties(
                base_temperature=22.0,
                conductivity=100.0,
                density=1000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
            entity.base_link_idx: gs.sensors.TemperatureProperties(
                base_temperature=200.0,
                conductivity=1000.0,
                density=2000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
        },
        ambient_temperature=22.0,
        convection_coefficient=0.0,
        draw_debug=True,
    )
)

scene.build()

grid = temperature_sensor.read()
print(grid)  # shape ([n_envs,] nx, ny, nz)
```

Set `simulate_all_link_temperatures=True` if you want Genesis to evolve temperatures for every link with thermal properties, not just the sensor-attached link.

The example `examples/sensors/temperature_grid.py` visualizes a hot pusher heating a platform while objects are dropped onto the sensorized surface.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/temperaturegrid.mp4" type="video/mp4">
</video>