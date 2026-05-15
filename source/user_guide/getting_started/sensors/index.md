# 🖲️ Sensors

In Genesis, a sensor extracts information from the scene without affecting it. Sensors model the **robot-control view** of an onboard sensor: each is sampled at its own rate, stamped with optional noise / drift / delay / jitter, and read back as a tensor. Reads are idempotent within a step - two `read()` calls inside one control-loop timestep return the same value.

Setting `history_length=N` on the options returns the last `N` snapshots stacked along a new axis (shape becomes `(B, N, *return_shape)`, index 0 = current). Each snapshot keeps the imperfection state it had at capture time, so delayed reads are physically consistent.

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
        history_length=4,   # omit (or set to 0) for the current snapshot only
        draw_debug=True,
    )
)

scene.build(n_envs=16)
for _ in range(1000):
    scene.step()

    # Measured value (with imperfections, if any), shape (16, 4, 1).
    is_touching = contact.read()

    # Noiseless ground truth, same shape.
    is_touching_gt = contact.read_ground_truth()
```

For high-throughput RL or logging, `scene.read_sensors()` and `entity.read_sensors()` return one batched tensor per sensor class - a single bulk call that covers every sensor in scope. The last axis is a flat concatenation of every sensor of that class (for `NamedTuple`-returning sensors, the fields are packed in order: an IMU contributes `lin_acc + ang_vel + mag = 9` scalars). The history axis is present whenever any sensor in the class was created with `history_length > 0`:

```python
# dict[sensor_class, tensor]
data = scene.read_sensors()

# No history on the IMU class: shape (B, N_imus * 9).
imu_batch = data[gs.sensors.types.IMU]

# history_length=4 on the Contact sensor above: shape (B, 4, N_contacts).
contact_batch = data[gs.sensors.types.Contact]
```

For the design of the sensor pipeline and how to add your own sensor type, see {doc}`Extending Genesis → Sensors <../../advanced_topics/sensors/index>`.

Example scripts live under `examples/sensors/`.

## Sensor families

- [**🧭 IMU**](imu) - accelerometer and gyroscope, with noise / drift / delay / jitter.
- [**🫳 Contact & Tactile**](contact_and_tactile) - boolean contact, contact force, penetration-based probes, elastomer displacement.
- [**📡 Raycaster Sensors**](raycaster) - Lidar and depth camera with `SphericalPattern`, `DepthCameraPattern`, `GridPattern`.
- [**🎥 Camera Sensors**](camera_sensors) - rasterizer, ray-tracer, and Madrona batch renderer for RGB / depth / segmentation / normal.
- [**📏 Proximity**](proximity) - nearest-distance probes to tracked mesh surfaces.
- [**🌡️ Temperature Grid**](temperature_grid) - voxelized temperature field on a rigid link, with conduction / radiation / convection.

For saving sensor data alongside the simulation, see [Recorders](../recorders).

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
