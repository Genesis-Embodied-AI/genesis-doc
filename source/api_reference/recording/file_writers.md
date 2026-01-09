# File Writers

Genesis provides file writers for exporting simulation data to various formats.

## Available Writers

| Writer | Format | Description |
|--------|--------|-------------|
| `CSVFileWriter` | `.csv` | Tabular data export |
| `NPZFileWriter` | `.npz` | NumPy compressed arrays |
| `VideoFileWriter` | `.mp4` | Video from camera/viewer |

## CSVFile

Export data as comma-separated values:

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Record joint positions to CSV
scene.start_recording(
    data_func=lambda: {
        "q0": robot.get_qpos()[0],
        "q1": robot.get_qpos()[1],
        "q2": robot.get_qpos()[2],
    },
    rec_options=gs.recorders.CSVFile(
        filepath="joint_data.csv",
        hz=100,
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

## NPZFile

Export data as NumPy compressed archive:

```python
scene.start_recording(
    data_func=lambda: {
        "pos": robot.get_pos(),
        "qpos": robot.get_qpos(),
        "qvel": robot.get_qvel(),
    },
    rec_options=gs.recorders.NPZFile(
        filepath="trajectory.npz",
        hz=50,
    ),
)

# ... simulation ...
scene.stop_recording()

# Load recorded data
import numpy as np
data = np.load("trajectory.npz")
positions = data["pos"]
```

## VideoFile

Record video from cameras or viewer:

```python
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

scene.start_recording(
    data_func=lambda: cam.render(rgb=True),
    rec_options=gs.recorders.VideoFile(
        filepath="simulation.mp4",
    ),
)

for i in range(300):
    scene.step()
scene.stop_recording()
```

## Configuration Options

### Common Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `filepath` | str | Required | Output file path |
| `hz` | float | None | Recording frequency |
| `async_mode` | bool | False | Background processing |

### VideoFileWriter Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fps` | int | 30 | Video frame rate |
| `codec` | str | "libx264" | Video codec |

## API Reference

```{eval-rst}
.. automodule:: genesis.recorders.file_writers
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Recording overview
- {doc}`plotters` - Real-time visualization
