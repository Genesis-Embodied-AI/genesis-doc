# Recording data

A **recorder** samples data from your simulation on a schedule and processes it for you (writing it to a file or drawing it in a live plot) without you threading logging code through your step loop. You describe *what* to record and *how*, then step the scene as usual.

Recording runs on a background thread by default, so it adds little overhead to the simulation itself.

The complete runnable example for this page is [`examples/sensors/imu_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/imu_franka.py), which logs an IMU sensor to an `.npz` file and plots it live:

```python
scene.start_recording(
    data_func=lambda: imu.read()._asdict(),
    rec_options=gs.recorders.NPZFile(filename="imu_data.npz"),
)
```

That single call captures IMU readings every step and writes them to `imu_data.npz` when recording stops.

## How recording works

Every scene owns a **RecorderManager**. Each call to `start_recording` registers one **recorder** with that manager, pairing two things:

- A **data function:** a zero-argument callable that returns the data to capture (a scalar, an array, or a `dict` of them).
- A **recorder options** object from `gs.recorders`, the *what to do with it*: a file writer or a plotter.

From then on, the manager drives the recorder for you:

1. On `scene.build()`, every registered recorder is built and started (files are opened, plot windows appear).
2. On each `scene.step()`, the manager calls the data function and hands the result to the recorder at the configured rate.
3. On `scene.stop_recording()` (or when the scene is destroyed), every recorder flushes and closes cleanly.

Because the manager reads the data function itself, you never call it in your loop. You describe the recording once, before build, and step normally.

:::{warning}
Set up all recording **before** `scene.build()`. `start_recording` asserts the scene is unbuilt and raises otherwise, because recorders allocate their file handles and windows during the build.
:::

## Recording sensor data

For a {doc}`sensor <index>`, `sensor.start_recording` is the shortest path: it uses the sensor's own `read()` as the data function, so you only pass the recorder options.

```python
imu = scene.add_sensor(gs.sensors.IMU(entity_idx=franka.idx))
imu.start_recording(gs.recorders.NPZFile(filename="imu_data.npz"))
```

## Recording arbitrary data

To record anything else, or to combine or preprocess sensor output, use `scene.start_recording` with your own data function. It takes the callable first and the recorder options second:

```python
def data_func():
    data = imu.read()
    true_data = imu.read_ground_truth()
    return {
        "lin_acc": data.lin_acc,  # measured, with noise
        "true_lin_acc": true_data.lin_acc,  # ground truth, for comparison
        "ang_vel": data.ang_vel,
        "true_ang_vel": true_data.ang_vel,
    }

scene.start_recording(
    data_func,
    gs.recorders.MPLLinePlot(
        title="IMU Data",
        labels={
            "lin_acc": ("x", "y", "z"),
            "true_lin_acc": ("x", "y", "z"),
            "ang_vel": ("x", "y", "z"),
            "true_ang_vel": ("x", "y", "z"),
        },
    ),
)
```

A `dict` return value becomes one labeled subplot per key. The result is a live plot that updates as the scene steps:

<video preload="auto" controls width="100%">
<source src="../../_static/videos/imu.mp4" type="video/mp4">
Live matplotlib line plot of IMU linear acceleration and angular velocity, measured against ground truth.
</video>

## Available recorders

Pass any of these to `start_recording` as the recorder options. All are exported from `gs.recorders`.

**File writers** persist data to disk:

| Recorder | Writes | Notes |
|---|---|---|
| `NPZFile` | `.npz` | Buffers everything and writes once at stop. Handles arrays and dicts of arrays. |
| `CSVFile` | `.csv` | One row per sample. Pass `header` to name columns; `save_every_write=True` to flush continuously. |
| `VideoFile` | `.mp4` | Streams frames straight to file via PyAV. Data must be a `[H, W]` or `[H, W, 3]` `uint8` image. |

**Plotters** visualize data live, and can also save the animation via `save_to_filename`:

| Recorder | Shows | Data shape |
|---|---|---|
| `PyQtLinePlot` | Live line plot (PyQtGraph) | scalars, tuples, or dicts of them |
| `MPLLinePlot` | Live line plot (matplotlib) | scalars, tuples, or dicts of them |
| `MPLImagePlot` | Live image | `(H, W)`, `(H, W, 1/3/4)` |
| `MPLVectorFieldPlot` | 3D vectors projected to a plane, colored by magnitude | `(N, 3)` at fixed `positions` |

`PyQtGraph` and `matplotlib` are optional dependencies. The example probes for them and falls back gracefully. See `IS_PYQTGRAPH_AVAILABLE` / `IS_MATPLOTLIB_AVAILABLE` in `genesis.recorders.plotters`.

For more usage: camera video and image recording in [`examples/manipulation/grasp_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/manipulation/grasp_env.py), joint-torque plotting in [`examples/sensors/joint_torque_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/joint_torque_franka.py), and tactile vector fields in [`examples/sensors/tactile_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_franka.py).

## Sampling rate and buffering

Every recorder options object accepts a few shared settings:

- `hz`: how often to sample, in samples per second. If omitted, the data function runs every step. Genesis World snaps `hz` to the nearest integer multiple of the timestep and warns if it had to adjust.
- `save_on_reset` (file writers): when `True`, `scene.reset()` flushes the current file and appends an incrementing counter to the filename, starting a fresh recording per episode.
- `buffer_size` and `buffer_full_wait_time`: bound the background queue used when recording off-thread.

```python
scene.start_recording(
    data_func=lambda: franka.get_qpos(),
    rec_options=gs.recorders.NPZFile(filename="qpos.npz", hz=50),  # 50 samples/second
)
```

## Stopping recording

Recording stops automatically when the scene is destroyed, so short scripts need no explicit teardown. Call `scene.stop_recording()` to stop and flush every recorder early, for example to finalize a file before the program continues:

```python
scene.stop_recording()  # flushes files, closes plot windows
```

## See also

- {doc}`Recording API reference </api_reference/recording/index>`: `RecorderManager`, `Recorder`, and every recorder options class.
- {doc}`Sensors <index>`: the contact, tactile, surface distance, IMU, and temperature sensors you can record from.
- {doc}`Camera sensors <camera_sensors>`: RGB, depth, segmentation, and normal outputs, which pair with `VideoFile` and `MPLImagePlot`.
