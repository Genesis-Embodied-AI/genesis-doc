# Recording and playback

Genesis World records simulation data through a recorder framework: you register a recorder with the scene, describe *what* to sample, then step the scene as usual. The recorder samples on a schedule and either writes the data to a file or draws it in a live plot, so you never thread logging code through your step loop.

This page is the API overview for the `genesis.recorders` module. For a task-oriented walkthrough, see {doc}`/user_guide/sensing/recorders`.

## Components

- **Recorder:** the base class that processes each sampled value. See {doc}`recorder`.
- **RecorderManager:** the per-scene coordinator that drives every registered recorder as the scene builds, steps, and resets. See {doc}`recorder_manager`.
- **File writers:** `NPZFile`, `CSVFile`, and `VideoFile` persist data to disk. See {doc}`file_writers`.
- **Plotters:** `PyQtLinePlot`, `MPLLinePlot`, `MPLImagePlot`, and `MPLVectorFieldPlot` visualize data live and can save the animation. See {doc}`plotters`.

All recorder options classes are exported from `gs.recorders`.

## Workflow

Register a recorder with `scene.start_recording` before `scene.build()`, passing a zero-argument data function and a recorder options object from `gs.recorders`. The manager samples the data function on each step and either writes it to a file or draws it in a live plot. A `dict` return value becomes one labeled subplot per key. Recording stops and flushes on `scene.stop_recording()`, or automatically when the scene is destroyed.

A camera exposes its own recording path, separate from the recorder framework: it buffers every frame produced by `cam.render()` between `cam.start_recording()` and `cam.stop_recording(...)`, then writes them to a video file. Unlike `scene.start_recording`, `cam.start_recording` requires a built scene.

For usage, see {doc}`/user_guide/sensing/recorders`.

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

- {doc}`/user_guide/sensing/recorders`: task-oriented guide to recording sensor and custom data.
- {doc}`/api_reference/visualization/index`: cameras and other visual output.
- {doc}`/api_reference/scene/index`: `scene.start_recording` and `scene.stop_recording`.
