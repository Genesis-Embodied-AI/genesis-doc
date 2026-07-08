# Sensors

A sensor extracts information from a scene without modifying its physics. It models the robot-control view of an onboard device: attach it to a link, step the simulation, and read back a tensor. Genesis World ships sensors for contact and force, inertial measurement, ranging, rendering, proximity, and temperature.

## The attach-and-read model

Create a sensor with `scene.add_sensor()`, passing an options object from `gs.sensors`. The call returns a sensor handle you keep and read each step. Most sensors attach to a rigid link through `entity_idx` and `link_idx_local`; a few are static or bound to a whole entity.

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FL_foot").idx_local,
        history_length=4,  # keep the last 4 snapshots; omit for the current one only
        draw_debug=True,
    )
)

scene.build(n_envs=16)
for _ in range(1000):
    scene.step()

    measured = contact.read()               # with imperfections, shape (16, 4, 1)
    ground_truth = contact.read_ground_truth()  # noiseless, same shape
```

Every sensor exposes two reads:

- `read()` returns the measured value, with the sensor's imperfections applied (delay and jitter always; noise, bias, and drift where the sensor models them, as the {doc}`imu` does).
- `read_ground_truth()` returns the noiseless value with the same shape.

Reads are idempotent within a step: two calls in one control-loop timestep return the same value, because the value is computed once per `scene.step()`.

Set `history_length=N` on the options to keep the last `N` snapshots, stacked along a new axis inserted after the batch axis (index 0 is the current step). Each snapshot retains the imperfection state it had when captured, so delayed reads stay physically consistent.

## Parallel and heterogeneous environments

Sensors run across parallel environments. A returned tensor carries a leading batch axis, written `([n_envs,] ...)`: the `[n_envs,]` bracket is present when the scene is built with multiple environments and absent otherwise. The example above reads shape `(16, 4, 1)` — 16 environments, 4 history steps, 1 contact bin.

For high-throughput training or logging, read every sensor of a class at once with `scene.read_sensors()` (or `entity.read_sensors()` to scope it to one entity). Each returns a `dict` keyed by a sensor-type tag, `gs.sensors.types.<Name>`, mapping to one batched tensor per class. The last axis is a flat concatenation of every sensor of that class; for sensors that return a `NamedTuple`, the fields are packed in field order (an {doc}`imu` contributes `lin_acc + ang_vel + mag = 9` scalars). The history axis is present whenever any sensor in the class was created with `history_length > 0`.

```python
data = scene.read_sensors()  # dict[sensor-type tag, tensor]

# No history on the IMU class: shape ([n_envs,] n_imus * 9).
imu_batch = data[gs.sensors.types.IMU]

# history_length=4 on the Contact sensor above: shape ([n_envs,] 4, n_contacts).
contact_batch = data[gs.sensors.types.Contact]
```

## Sensor types

Each family has its own page. The `read()` return types and shapes below are the per-sensor outputs; the bulk `read_sensors()` tensors flatten these along the last axis.

| Page | Options classes (`gs.sensors.*`) | Measures | `read()` returns |
|---|---|---|---|
| {doc}`imu` | `IMU` | linear acceleration, angular velocity, magnetic field | `IMUReturnType(lin_acc, ang_vel, mag)`, each `([n_envs,] 3)` |
| {doc}`contact_and_tactile` | `Contact`, `ContactForce`, `KinematicTaxel`, `ElastomerTaxel`, `ProximityTaxel` | contact state, net force, per-taxel force/torque and displacement | bool `([n_envs,] 1)`; force `([n_envs,] 3)`; per-taxel `force`/`torque` `([n_envs,] n_probes, 3)` |
| {doc}`raycaster` | `Lidar` (alias of `Raycaster`), `DepthCamera` | ray-hit points and distances | `RaycasterReturnType(points, distances)`: points `([n_envs,] *pattern_shape, 3)`, distances `([n_envs,] *pattern_shape)` |
| {doc}`camera_sensors` | `RasterizerCameraSensor`, `RaytracerCameraSensor`, `BatchRendererCameraSensor` | rendered RGB images | `CameraReturnType(rgb)`, shape `([n_envs,] height, width, 3)` |
| {doc}`proximity` | `SurfaceDistanceProbe` | nearest distance from probes to tracked mesh surfaces | distances `([n_envs,] n_probes)`; `sensor.nearest_points` `([n_envs,] n_probes, 3)` |
| {doc}`temperature_grid` | `TemperatureGrid` | per-cell temperature in Celsius over a voxel grid | `([n_envs,] grid_x, grid_y, grid_z)` |

Genesis World also ships `gs.sensors.JointTorque`, which reports actuator output effort per dof (shape `([n_envs,] n_dofs)`); see `examples/sensors/joint_torque_franka.py`.

Runnable examples for every sensor live under `examples/sensors/`.

## See also

- {doc}`Recorders </user_guide/getting_started/recorders>` — save sensor data alongside the simulation.
- {doc}`Extending Genesis World: sensors </user_guide/advanced_topics/sensors/index>` — the sensor pipeline and how to add your own sensor type.

```{toctree}
:hidden:
:maxdepth: 1

imu
contact_and_tactile
raycaster
camera_sensors
proximity
temperature_grid
```
