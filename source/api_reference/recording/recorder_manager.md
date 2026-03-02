# RecorderManager

The `RecorderManager` coordinates multiple recorders, handling their lifecycle and data distribution.

## Overview

The RecorderManager:

- Manages a collection of recorders
- Dispatches data to appropriate recorders
- Handles start/stop of recording sessions
- Coordinates build and cleanup phases

## Usage

The RecorderManager is typically accessed through the Scene:

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Add multiple recorders
scene.add_recorder(
    gs.recorders.NPZFileWriter(filepath="data.npz"),
    data_func=lambda: robot.get_qpos(),
)

scene.add_recorder(
    gs.recorders.MPLLinePlotter(title="Positions"),
    data_func=lambda: robot.get_qpos(),
)

# Start all recorders
scene.start_recording()

for i in range(1000):
    scene.step()

# Stop all recorders
scene.stop_recording()
```

## Recording Controls

```python
# Start recording all registered recorders
scene.start_recording()

# Check recording status
if scene.is_recording:
    print("Currently recording")

# Stop recording and trigger cleanup
scene.stop_recording()

# Stop recording and save video (if viewer is active)
scene.stop_recording(save_to="output.mp4")
```

## API Reference

```{eval-rst}
.. autoclass:: genesis.recorders.recorder_manager.RecorderManager
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`recorder` - Base recorder class
- {doc}`/api_reference/scene/scene` - Scene recording methods
