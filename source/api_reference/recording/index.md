# Recording and playback

Genesis World records simulation data through a recorder framework: you register a recorder with the scene, describe *what* to sample, then step the scene as usual. The recorder samples on a schedule and either writes the data to a file or draws it in a live plot, so you never thread logging code through your step loop.

This page is the API overview for the `genesis.recorders` module. For a task-oriented walkthrough, see {doc}`/user_guide/getting_started/recorders`.

## Components

- **Recorder:** the base class that processes each sampled value. See {doc}`recorder`.
- **RecorderManager:** the per-scene coordinator that drives every registered recorder as the scene builds, steps, and resets. See {doc}`recorder_manager`.
- **File writers:** `NPZFile`, `CSVFile`, and `VideoFile` persist data to disk. See {doc}`file_writers`.
- **Plotters:** `PyQtLinePlot`, `MPLLinePlot`, `MPLImagePlot`, and `MPLVectorFieldPlot` visualize data live and can save the animation. See {doc}`plotters`.

All recorder options classes are exported from `gs.recorders`.

## Minimal example

Register a recorder with `scene.start_recording` before `scene.build()`, passing a zero-argument data function and a recorder options object. The manager samples the data function for you on each step.

```python
import genesis as gs

gs.init()
scene = gs.Scene()
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))

scene.start_recording(
    data_func=lambda: franka.get_qpos(),
    rec_options=gs.recorders.NPZFile(filename="qpos.npz", hz=50),  # 50 samples/second
)

scene.build()

for _ in range(1000):
    scene.step()

scene.stop_recording()  # flushes files and closes plot windows
```

Recording also stops and flushes when the scene is destroyed, so short scripts need no explicit `stop_recording`.

## Recording a live plot

Swap the file writer for a plotter to visualize data as it is produced. A `dict` return value becomes one labeled subplot per key.

```python
scene.start_recording(
    data_func=lambda: franka.get_qpos(),
    rec_options=gs.recorders.MPLLinePlot(title="Joint positions"),
)
```

## Recording camera video

A camera exposes its own recording path, separate from the recorder framework. It buffers every frame produced by `cam.render()` while recording is active, then writes them to a video file on stop. Unlike `scene.start_recording`, `cam.start_recording` requires a built scene.

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 1), size=(1.0, 1.0, 1.0)))
cam = scene.add_camera(res=(640, 480), pos=(3, 0, 2), lookat=(0, 0, 0.5))

scene.build()

cam.start_recording()
for _ in range(200):
    scene.step()
    cam.render()
cam.stop_recording(save_to_filename="simulation.mp4", fps=60)
```

## Components reference

```{toctree}
:titlesonly:

recorder
recorder_manager
file_writers
plotters
```

## Shared options

Every recorder options class inherits these fields from `RecorderOptions`:

| Option | Type | Default | Description |
|---|---|---|---|
| `hz` | float or `None` | `None` | Sampling frequency in samples per second. If `None`, samples on every step. Snapped to the nearest integer multiple of the timestep. |
| `buffer_size` | int | `0` | Size of the background queue used when a recorder runs off-thread. `0` means unbounded. |
| `buffer_full_wait_time` | float | `0.1` s | How long to wait for queue space when the buffer is full. |

File writers (`NPZFile`, `CSVFile`, `VideoFile`) add one more shared field:

- **`save_on_reset`:** when `True`, `scene.reset()` flushes the current file and appends an incrementing counter to the filename, starting a fresh recording per episode. Defaults to `False`.

:::{note}
Whether a recorder runs on a background thread is decided internally per recorder through its `run_in_thread` property; it is not a user-facing option. The `buffer_size` and `buffer_full_wait_time` settings apply only to recorders that run off-thread.
:::

## See also

- {doc}`/user_guide/getting_started/recorders` — task-oriented guide to recording sensor and custom data.
- {doc}`/api_reference/visualization/index` — cameras and other visual output.
- {doc}`/api_reference/scene/index` — `scene.start_recording` and `scene.stop_recording`.
