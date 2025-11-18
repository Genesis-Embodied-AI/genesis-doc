# 🎥 Saving and Visualizing Data with Recorders
Genesis also provides data recording utilities for automatically processing data without slowing down the simulation.
This can be used to stream formatted data to a file, or visualize the data live.

```python
# 1. Start recording before building scene
sensor.start_recording(
    rec_options=gs.recorders.NPZFile(
        filename="sensor_data.npz"
    ),
)
```
... And that's it! Recordings will automatically stop and clean up when the scene is no longer active, and can also
be stopped with `scene.stop_recording()`.

You can record sensor data with `sensor.start_recording(recorder_options)` or any other kind of data using `scene.start_recording(data_func, recorder_options)` with a custom data function. For example:

```
def imu_data_func():
    data = imu.read()
    true_data = imu.read_ground_truth()
    return {
        "lin_acc": data.lin_acc,
        "true_lin_acc": true_data.lin_acc,
        "ang_vel": data.ang_vel,
        "true_ang_vel": true_data.ang_vel,
    }

scene.start_recording(
    imu_data_func,
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

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/imu.mp4" type="video/mp4">
</video>

See RecorderOptions in the API reference for currently available recorders.
More example uses of recorders can also be seen in `examples/sensors/`. 