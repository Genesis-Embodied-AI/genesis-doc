# Recording data

A **recorder** samples data from your simulation on a schedule and processes it for you (writing it to a file or drawing it in a live plot) without you threading logging code through your step loop. Describe *what* to record and *how*, then step the scene as usual.

Recording runs on a background thread by default, so it adds little overhead to the simulation itself.

The complete runnable example for this page is [`examples/sensors/imu_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/imu_franka.py), which logs an IMU sensor to an `.npz` file and plots it live:

```python
scene.add_recorder(
    data_func=lambda: imu.read()._asdict(),
    rec_options=gs.recorders.NPZFile(filename="out/imu_data.npz"),
)
```

That single call captures IMU readings every step and writes them to `out/imu_data.npz` when recording stops.

## How recording works

Every scene owns a **RecorderManager**. Each call to `add_recorder` registers one **recorder** with that manager, pairing two things:

- A **data function:** a zero-argument callable that returns the data to capture (a scalar, an array, or a `dict` of them).
- A **recorder options** object from `gs.recorders`, the *what to do with it*: a file writer or a plotter.

From then on, the manager drives the recorder for you:

1. On `scene.build()`, the manager builds and starts every registered recorder: files open, plot windows appear.
2. Before each `scene.step()`, the manager calls the data function and hands the result to the recorder at the configured rate. A sample is therefore the state a step starts from, with the control inputs the step consumes, whether a setter or a pre-step callback wrote them.
3. On `scene.stop_recording()` (or when the scene is destroyed), the manager records the state the run stopped at, whatever the sampling rate, then every recorder flushes and closes cleanly. A reset of the whole scene records the state it leaves behind the same way.

Because the manager reads the data function itself, you never call it in your loop. Describe the recording once, before build, and step normally.

:::{warning}
Set up all recording **before** `scene.build()`. `scene.add_recorder`, `scene.start_recording`, and `sensor.start_recording` assert the scene is unbuilt and raise otherwise, because recorders allocate their file handles and windows during the build.
:::

A visualization camera has its own video API, `camera.start_recording()`, which you call *after* build and which bypasses the recorder manager entirely; see {doc}`Recording a video </user_guide/rendering/cameras>`. `scene.start_recording` records the scene itself, every array of its simulation at every step, to a file that replays it; see {doc}`Checkpoints and simulation state </user_guide/configuration/checkpoints>`.

## Recording sensor data

For a {doc}`sensor <index>`, `sensor.start_recording` is the shortest path: it uses the sensor's own `read()` as the data function, so you only pass the recorder options.

```python
imu = scene.add_sensor(gs.sensors.IMU(entity_idx=franka.idx))
imu.start_recording(gs.recorders.NPZFile(filename="out/imu_data.npz"))
```

## Recording arbitrary data

To record anything else, or to combine or preprocess sensor output, use `scene.add_recorder` with your own data function. It takes the callable first and the recorder options second:

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

scene.add_recorder(
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

Pass any of these to `add_recorder` as the recorder options. All are exported from `gs.recorders`.

**File writers** persist data to disk:

| Recorder | Writes | Notes |
|---|---|---|
| {py:class}`NPZFile <genesis.options.recorders.NPZFile>` | `.npz` | Buffers everything and writes once at stop. Handles arrays and dicts of arrays. |
| {py:class}`CSVFile <genesis.options.recorders.CSVFile>` | `.csv` | One row per sample. Pass `header` to name columns; `save_every_write=True` to flush continuously. |
| {py:class}`VideoFile <genesis.options.recorders.VideoFile>` | `.mp4` | Streams frames straight to file via PyAV. Data must be a `[H, W]` or `[H, W, 3]` `uint8` image. |
| {py:class}`TrajectoryFile <genesis.options.recorders.TrajectoryFile>` | `.gstraj` | The state of the scene itself, one frame per step, for `gs.Scene.load_trajectory` to seek and replay. Registered with `scene.start_recording`, since the scene is the data source. |

**Plotters** visualize data live, and can also save the animation via `save_to_filename`:

| Recorder | Shows | Data shape |
|---|---|---|
| {py:class}`PyQtLinePlot <genesis.options.recorders.PyQtLinePlot>` | Live line plot (PyQtGraph) | scalars, tuples, or dicts of them |
| {py:class}`MPLLinePlot <genesis.options.recorders.MPLLinePlot>` | Live line plot (matplotlib) | scalars, tuples, or dicts of them |
| {py:class}`MPLImagePlot <genesis.options.recorders.MPLImagePlot>` | Live image | `(H, W)`, `(H, W, 1/3/4)` |
| {py:class}`MPLVectorFieldPlot <genesis.options.recorders.MPLVectorFieldPlot>` | 3D vectors projected to a plane, colored by magnitude | `(N, 3)` at fixed `positions` |

`PyQtGraph` and `matplotlib` are optional dependencies. The example prefers `PyQtLinePlot`, falls back to `MPLLinePlot` when PyQtGraph is missing, and skips live plotting when neither is installed; it reads `IS_PYQTGRAPH_AVAILABLE` and `IS_MATPLOTLIB_AVAILABLE` from `genesis.recorders.plotters` to decide.

For more usage: camera video and image recording in [`examples/manipulation/grasp_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/manipulation/grasp_env.py), joint-torque plotting in [`examples/sensors/joint_torque_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/joint_torque_franka.py), and tactile vector fields in [`examples/sensors/tactile_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_franka.py).

## Sampling rate and buffering

Every recorder options object accepts a few shared settings:

- `hz`: how often to sample, in samples per second. If omitted, the data function runs every step. Genesis World snaps `hz` to the nearest integer multiple of the timestep and warns if it had to adjust.
- `buffer_size` and `buffer_full_wait_time`: bound the background queue used when recording off-thread. When the queue is full for longer than `buffer_full_wait_time`, the oldest sample is dropped.

```python
scene.add_recorder(
    data_func=lambda: franka.get_qpos(),
    rec_options=gs.recorders.NPZFile(filename="qpos.npz", hz=50),  # 50 samples/second
)
```

A failure of a recorder, a sample or a write that raises, such as a disk that fills up, is raised on the stepping thread: at once from `scene.step()` when the recorder runs there, at the next step or `sync()` when it runs on a background thread. The recorder that failed records no more, a reset of the scene restarts the others, and `scene.stop_recording()` still flushes what it wrote. A reset of the scene never starts a new file: the recording goes on in the same one, with the state re-initialized.

## Stopping recording

Recording stops automatically when the scene is destroyed, so short scripts need no explicit teardown. Call `scene.stop_recording()` to stop and flush every recorder early, for example to finalize a file before the program continues:

```python
scene.stop_recording()  # flushes files, closes plot windows
```

## See also

- {doc}`Recording API reference </api_reference/recording/index>`: `RecorderManager`, `Recorder`, and every recorder options class.
- {doc}`Sensors <index>`: the contact, tactile, surface distance, IMU, and temperature sensors you can record from.
- {doc}`Camera sensors <camera_sensors>`: RGB frames, which pair with `VideoFile` and `MPLImagePlot`.
