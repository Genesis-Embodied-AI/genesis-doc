# Sensors

Sensors read information out of a scene without changing its physics. You attach a sensor to a link, step the simulation, and read back a tensor each step. This page catalogs the sensor types and their return shapes; for the attach-and-read model, imperfections, history, and batched reads, see {doc}`the sensors guide </user_guide/sensing/index>`.

## Sensor types

Create a sensor with `scene.add_sensor()`, passing an options object from `gs.sensors`. The call returns a handle whose `read()` gives the measured value and `read_ground_truth()` the noiseless one, both with the same shape. Camera sensors can also be created through `scene.add_camera()`, documented on the {doc}`camera` page.

Shapes use the batched-optional notation `([n_envs,] ...)`: the leading `n_envs` axis is present when the scene is built with multiple environments and absent otherwise.

| `gs.sensors.*` | `read()` returns | Shape |
|---|---|---|
| `RasterizerCameraOptions`, `RaytracerCameraOptions`, `BatchRendererCameraOptions` | `CameraReturnType(rgb)`, `rgb` uint8 | `([n_envs,] height, width, 3)` |
| `Contact` | `torch.Tensor` (bool) | `([n_envs,] 1)` |
| `ContactForce` | `torch.Tensor` (float32) | `([n_envs,] 3)` |
| `IMU` | `IMUReturnType(lin_acc, ang_vel, mag)` (float32) | each `([n_envs,] 3)` |
| `Raycaster` (alias `Lidar`), `DepthCamera` | `RaycasterReturnType(points, distances)` (float32) | `points` `([n_envs,] *pattern_shape, 3)`, `distances` `([n_envs,] *pattern_shape)` |
| `SurfaceDistanceProbe` | `torch.Tensor` (float32) distances | `([n_envs,] n_probes)` |
| `ContactProbe` | `torch.Tensor` (bool) | `([n_envs,] n_probes)` |
| `ContactDepthProbe` | `torch.Tensor` (float32) penetration depth | `([n_envs,] n_probes)` |
| `KinematicTaxel` | `KinematicTaxelReturnType(force, torque)` (float32) | each `([n_envs,] n_probes, 3)` |
| `ElastomerTaxel` | `torch.Tensor` (float32) marker displacement | `([n_envs,] n_probes, 3)` |
| `ProximityTaxel` | `ProximityTaxelReturnType(force, torque)` (float32) | each `([n_envs,] n_probes, 3)` |
| `TemperatureGrid` | `torch.Tensor` (float32) | `([n_envs,] grid_x, grid_y, grid_z)` |
| `JointTorque` | `torch.Tensor` (float32) | `([n_envs,] n_dofs)` |

Notes on the return types:

- **Camera sensors:** `read()` returns `CameraReturnType`, which carries a single `rgb` field. Depth, segmentation, and surface normals come from `scene.add_camera(...).render(...)`, not from the camera-sensor `read()`.
- **`SurfaceDistanceProbe`:** `read()` returns the probe-to-surface distances; the corresponding nearest points are available as `sensor.nearest_points`, shape `([n_envs,] n_probes, 3)`.
- **`Raycaster` patterns:** `pattern_shape` follows the ray pattern: for example `(n_horizontal, n_vertical)` for a spherical pattern and `(height, width)` for `DepthCamera`.

## Quick start

Attach a camera, a contact-force sensor, and an IMU, then read each after a step.

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

contact_force = scene.add_sensor(
    gs.sensors.ContactForce(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FL_foot").idx_local,
    )
)

imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("base").idx_local,
    )
)

scene.build()

scene.step()

rgb, _, _, _ = cam.render(rgb=True)  # rgb: uint8, shape ([n_envs,] height, width, 3)
force = contact_force.read()         # float32, shape ([n_envs,] 3), Newtons in link frame
imu_data = imu.read()                # IMUReturnType(lin_acc, ang_vel, mag)
acceleration = imu_data.lin_acc      # shape ([n_envs,] 3)
angular_velocity = imu_data.ang_vel  # shape ([n_envs,] 3)
```

Runnable examples for every sensor live under `examples/sensors/`.

## Sensor reference pages

```{toctree}
:titlesonly:

camera
contact
imu
raycaster
tactile
other
```

## See also

- {doc}`/user_guide/sensing/index`: the attach-and-read model, imperfections, history, and batched reads.
- {doc}`/api_reference/visualization/index`: the rendering and camera system.
- {doc}`/api_reference/entity/index`: entities and links that sensors attach to.
