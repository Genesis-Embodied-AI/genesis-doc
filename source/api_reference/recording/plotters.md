# Plotters

Genesis provides real-time plotting recorders for visualizing simulation data during execution.

## Available Plotters

| Plotter | Description |
|---------|-------------|
| `MPLLinePlot` | Matplotlib line plot (time series) |
| `MPLImagePlot` | Matplotlib image display |

## MPLLinePlot

Real-time line plots using Matplotlib:

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Plot joint positions over time
scene.start_recording(
    data_func=lambda: robot.get_qpos()[:3],  # First 3 joints
    rec_options=gs.recorders.MPLLinePlot(
        title="Joint Positions",
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

### Configuration

```python
gs.recorders.MPLLinePlot(
    title="Plot Title",           # Plot title
    hz=30,                        # Update rate
)
```

## MPLImagePlot

Display images in real-time:

```python
cam = scene.add_camera(res=(320, 240), pos=(3, 0, 2), lookat=(0, 0, 0.5))

scene.start_recording(
    data_func=lambda: cam.render(rgb=True),
    rec_options=gs.recorders.MPLImagePlot(
        title="Camera View",
    ),
)

for i in range(500):
    scene.step()
scene.stop_recording()
```

## Multiple Recorders

You can start multiple recorders for different data streams by calling `start_recording` multiple times or using the RecorderManager directly.

## Performance Tips

1. **Reduce update rate**: Use lower `hz` for complex plots
2. **Limit data points**: Use smaller `window_size`
3. **Use async mode**: Enable `async_mode=True` for background updates

## API Reference

```{eval-rst}
.. automodule:: genesis.recorders.plotters
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Recording overview
- {doc}`file_writers` - File export
