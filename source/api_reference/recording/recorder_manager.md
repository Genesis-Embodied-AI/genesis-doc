# `RecorderManager`

The `RecorderManager` is the per-scene component that drives every recorder: it holds the registered recorders, samples their data functions as the scene steps, and flushes and closes them when recording stops. You do not construct or call it directly. You register recorders through `scene.start_recording` (or `sensor.start_recording`) and stop them through `scene.stop_recording`; the manager does the rest.

For a task-oriented walkthrough with runnable examples, see {doc}`/user_guide/sensing/recorders`. This page is the API reference.

## Registering recorders

Recorders are registered through the scene and its sensors, not on the manager. Each call pairs a zero-argument data function with a recorder options object from `gs.recorders`.

`scene.start_recording(data_func, rec_options)`
: Registers one recorder. `data_func` is a callable taking no arguments that returns the data to capture (a scalar, an array, or a `dict` of them); `rec_options` is a `RecorderOptions` instance that selects the recorder and configures it. Returns the created `Recorder`. Asserts the scene is **unbuilt** and raises otherwise, because recorders allocate their file handles and plot windows during `scene.build()`.

`sensor.start_recording(rec_options)`
: Shorthand for recording a {doc}`sensor </api_reference/sensor/index>`. It uses the sensor's own `read()` as the data function, so you pass only the options. Also asserts the scene is unbuilt.

`scene.stop_recording()`
: Stops and flushes every registered recorder, then clears them. Takes no arguments. Recording also stops automatically when the scene is destroyed, so short scripts need no explicit teardown.

There is no `scene.add_recorder` and no `scene.is_recording`; register with `start_recording` and let `build()` start the recorders for you.

## Camera video recording

Camera video capture is a separate mechanism from the recorder manager. A camera stores the RGB frames produced by `cam.render()` while recording is active and writes them to a video file. `cam.start_recording()` takes no arguments. `cam.stop_recording(save_to_filename=None, fps=60)` writes the stored frames; if `save_to_filename` is omitted the file is named after the calling script, the camera index, and a timestamp.

## Lifecycle and guarantees

- **Register before build.** `start_recording` must be called while the scene is unbuilt.
- **Started on build.** `scene.build()` builds and starts every registered recorder (files are opened, plot windows appear).
- **Sampled on step.** Each `scene.step()` samples the data functions at each recorder's configured rate (`rec_options.hz`, or every step if unset) and dispatches the data.
- **Flushed on stop.** `scene.stop_recording()`, or destroying the scene, flushes and closes every recorder cleanly.
- **Reset per episode.** `scene.reset()` resets the recorders; file writers with `save_on_reset=True` finalize the current file and start a fresh one.

## API reference

```{eval-rst}
.. autoclass:: genesis.recorders.recorder_manager.RecorderManager
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/sensing/recorders`: task-oriented guide to recording
- {doc}`recorder`: base recorder class
- {doc}`file_writers` and {doc}`plotters` - the recorder options you pass to `start_recording`
- {doc}`/api_reference/scene/scene`: `scene.start_recording` and `scene.stop_recording`
