# Recording and playback

Genesis World records simulation data through a recorder framework: you register a recorder with the scene, describe *what* to sample, then step the scene as usual. The recorder samples on a schedule and either writes the data to a file or draws it in a live plot, so you never thread logging code through your step loop.

This page is the API overview for the `genesis.recorders` module. For a task-oriented walkthrough, see {doc}`/user_guide/sensing/recorders`.

## Components

- **Recorder:** the base class that processes each sampled value. See {doc}`recorder`.
- **RecorderManager:** the per-scene coordinator that drives every registered recorder as the scene builds, steps, and resets. See {doc}`recorder_manager`.
- **File writers:** `NPZFile`, `CSVFile`, and `VideoFile` persist data to disk. See {doc}`file_writers`.
- **Plotters:** `PyQtLinePlot`, `MPLLinePlot`, `MPLImagePlot`, and `MPLVectorFieldPlot` visualize data live and can save the animation. See {doc}`plotters`.

All recorder options classes are exported from `gs.recorders`. For the recording workflow and worked examples, see {doc}`/user_guide/sensing/recorders`.

## Components reference

```{toctree}
:titlesonly:

recorder
recorder_manager
file_writers
plotters
```

## Shared options

Every recorder options class inherits these fields from `RecorderOptions`.

```{eval-rst}
.. autoclass:: genesis.options.recorders.RecorderOptions
```

## See also

- {doc}`/user_guide/sensing/recorders`: task-oriented guide to recording sensor and custom data.
- {doc}`/api_reference/visualization/index`: cameras and other visual output.
- {doc}`/api_reference/engine/index`: `scene.start_recording` and `scene.stop_recording`.
