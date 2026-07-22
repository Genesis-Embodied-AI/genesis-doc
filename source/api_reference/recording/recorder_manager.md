# RecorderManager

The `RecorderManager` is the per-scene component that drives every recorder: it holds the registered recorders, samples their data functions as the scene steps, and flushes and closes them when recording stops. You do not construct or call it directly. You register recorders through `scene.start_recording` (or `sensor.start_recording`) and stop them through `scene.stop_recording`; the manager does the rest.

For the recording workflow, registering recorders, and camera video capture, see {doc}`/user_guide/sensing/recorders`.

```{eval-rst}
.. autoclass:: genesis.recorders.recorder_manager.RecorderManager
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/sensing/recorders`: task-oriented guide to recording.
- {doc}`recorder`: base recorder class.
- {doc}`file_writers` and {doc}`plotters`: the recorder options you pass to `start_recording`.
- {doc}`/api_reference/engine/scene`: `scene.start_recording` and `scene.stop_recording`.
