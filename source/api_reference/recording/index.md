# Recording & Playback

Genesis provides a flexible recording system for capturing simulation data. This enables data logging, visualization, video generation, and analysis of simulation results.

## Overview

The recording system consists of:

- **Recorder**: Base class for processing simulation data
- **RecorderManager**: Coordinates multiple recorders
- **FileWriters**: Export data to files (CSV, NPZ, Video)
- **Plotters**: Real-time visualization of data

## Quick Start

### Recording Video

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 1)))
scene.build()

# Start recording
scene.start_recording()

for i in range(200):
    scene.step()
    scene.visualizer.update()

# Stop and save
scene.stop_recording(save_to="simulation.mp4")
```

### Recording Custom Data

```python
# Define what data to record
def get_robot_state():
    return {
        "position": robot.get_pos(),
        "velocity": robot.get_vel(),
        "joint_positions": robot.get_qpos(),
    }

# Start recording with recorder options
scene.start_recording(
    data_func=get_robot_state,
    rec_options=gs.recorders.NPZFile(
        filepath="robot_data.npz",
        hz=100,  # Recording frequency
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

### Real-time Plotting

```python
# Plot joint positions in real-time
scene.start_recording(
    data_func=lambda: robot.get_qpos(),
    rec_options=gs.recorders.MPLLinePlot(
        title="Joint Positions",
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

## Components

```{toctree}
:titlesonly:

recorder
recorder_manager
file_writers
plotters
```

## Recording Workflow

1. **Define data function**: A callable that returns the data to record
2. **Create recorder**: Instantiate a recorder (FileWriter, Plotter, etc.)
3. **Add to scene**: Register the recorder with the scene
4. **Start recording**: Begin data capture
5. **Run simulation**: Execute simulation steps
6. **Stop recording**: Finalize and save data

## Configuration

All recorders share common options:

| Option | Type | Description |
|--------|------|-------------|
| `hz` | float | Recording frequency (samples/second) |
| `async_mode` | bool | Process data in background thread |

## See Also

- {doc}`/api_reference/visualization/index` - Visual output
- {doc}`/api_reference/scene/index` - Scene management
