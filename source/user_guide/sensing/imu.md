# IMU

An **inertial measurement unit (IMU)** reports the motion of a rigid link as an onboard sensor would: linear acceleration from an accelerometer, angular velocity from a gyroscope, and, optionally, the local magnetic field from a magnetometer. Use it to feed state estimators, train locomotion policies on realistic proprioception, or log ground-truth dynamics.

The complete script is [`examples/sensors/imu_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/imu_franka.py). This page explains what the sensor measures and how to configure it; see {doc}`Sensors <index>` for the pipeline every sensor shares.

## Minimal example

An IMU is attached to one link of a rigid entity. Identify the link by its owning entity and the link's local index, then read the sensor after the scene is built:

```python
end_effector = franka.get_link("hand")

imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
    )
)

scene.build()

for _ in range(1000):
    scene.step()
    data = imu.read()  # IMUReturnType(lin_acc, ang_vel, mag)
    acc = data.lin_acc  # m/s^2, shape ([n_envs,] 3)
```

`read()` returns an `IMUReturnType` NamedTuple with fields `lin_acc`, `ang_vel`, and `mag`, each a tensor of shape `([n_envs,] 3)` in the sensor body frame. See {doc}`the IMU reference </api_reference/engine/sensors/imu>` for the units and full type.

## Frame and conventions

All three fields are expressed in the **sensor's body frame**, the frame of the attached link, rotated by any `euler_offset` you supply. They are not in the world frame, so they rotate with the link.

The accelerometer reports **specific force**: coordinate acceleration minus gravity. A sensor at rest therefore reads roughly `(0, 0, 9.81)` m/s² (the reaction to gravity along its local up axis), not zero. This matches real hardware, which cannot distinguish free fall from weightlessness.

When `pos_offset` moves the sensor off the link's origin, Genesis World adds the tangential and centripetal terms (`α × r` and `ω × (ω × r)`), so a spinning link produces the acceleration an IMU would actually feel at that offset.

## Attaching and offsetting the sensor

`entity_idx` and `link_idx_local` place the sensor on a link; `pos_offset` and `euler_offset` move and rotate it relative to that link's frame:

```python
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        pos_offset=(0.0, 0.0, 0.15),  # meters, in the link frame
        # euler_offset=(0, 0, 0),     # extrinsic x-y-z, degrees
        draw_debug=True,              # draw acc/gyro/mag arrows in the viewer
    )
)
```

With `draw_debug=True`, the viewer shows three arrows at the sensor: red for acceleration, green for angular velocity, blue for the magnetic field.

## Modeling sensor imperfections

By default the IMU is ideal. Each channel (`acc_*`, `gyro_*`, and `mag_*`) takes the same family of parameters to reproduce real-hardware error, applied per axis:

```python
imu = scene.add_sensor(
    gs.sensors.IMU(
        entity_idx=franka.idx,
        link_idx_local=end_effector.idx_local,
        pos_offset=(0.0, 0.0, 0.15),
        # noise parameters
        acc_cross_axis_coupling=(0.0, 0.01, 0.02),
        gyro_cross_axis_coupling=(0.03, 0.04, 0.05),
        acc_noise=(0.01, 0.01, 0.01),
        gyro_noise=(0.01, 0.01, 0.01),
        acc_random_walk=(0.001, 0.001, 0.001),
        gyro_random_walk=(0.001, 0.001, 0.001),
        delay=0.01,
        jitter=0.01,
        draw_debug=True,
    )
)
```

Each channel takes the same family of knobs: `*_noise` (white-noise standard deviation), `*_bias` (constant offset), `*_random_walk` (drift standard deviation), `*_cross_axis_coupling` (axis misalignment), and `*_resolution` (quantization step), plus the shared `delay` and `jitter` timing. Their exact meanings and defaults are in {doc}`the IMU reference </api_reference/engine/sensors/imu>` and the {doc}`sensors overview <index>`; set them from your target hardware's datasheet.

The magnetometer also reads a global field, set by `magnetic_field` (default `(0.0, 0.0, 0.5)` T in the world frame) and returned in the body frame.

## Reading measured versus ground-truth data

`read()` returns the value with all configured imperfections applied. `read_ground_truth()` returns the same quantities with no noise, bias, drift, or delay, which is useful as a training target or for validation:

```python
print("Ground truth data:")
print(imu.read_ground_truth())
print("Measured data:")
print(imu.read())
```

Both accept an optional `envs_idx` to select a subset of environments, and both are idempotent within a step: repeated calls in one control-loop timestep return the same value.

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/imu.mp4" type="video/mp4">
Your browser does not support the video tag; the clip shows the IMU arrows tracking a Franka end effector as it traces a circle.
</video>

## See also

- {doc}`Sensors <index>`: the shared read/record pipeline, `history_length`, and batched `read_sensors()`.
- {doc}`/user_guide/sensing/recorders`: save IMU streams alongside the simulation.
