# File writers

A file writer records sampled data to disk. Pass one as the `rec_options` argument of `scene.add_recorder`, and the recorder manager samples your data function on schedule and writes each sample to the file. See {doc}`index` for the recording workflow and the shared options (`hz`, `buffer_size`, `buffer_full_wait_time`) that every writer inherits.

## `gs.recorders.NPZFile`

Writes samples to a NumPy `.npz` archive. Best for numeric arrays you load back with `numpy.load`.

```{eval-rst}
.. autoclass:: genesis.options.recorders.NPZFile

.. autoclass:: genesis.recorders.file_writers.NPZFileWriter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.CSVFile`

Writes samples as rows in a `.csv` file. Best for scalar or low-dimensional data you inspect in a spreadsheet.

```{eval-rst}
.. autoclass:: genesis.options.recorders.CSVFile

.. autoclass:: genesis.recorders.file_writers.CSVFileWriter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.VideoFile`

Encodes a stream of image frames to a video file. Pair it with a data function that returns a rendered frame.

```{eval-rst}
.. autoclass:: genesis.options.recorders.VideoFile

.. autoclass:: genesis.recorders.file_writers.VideoFileWriter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.TrajectoryFile`

Records the state of the scene itself, one frame per step, to a `.gstraj` file. Register it with `scene.start_recording`, which takes the options alone since the scene is the data source, and open the file with `gs.Scene.load_trajectory` to seek and replay it. See {doc}`/user_guide/configuration/checkpoints` for the workflow.

```{eval-rst}
.. autoclass:: genesis.options.recorders.TrajectoryFile

.. autoclass:: genesis.recorders.trajectory.TrajectoryFileWriter
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.recorders.trajectory.Trajectory
    :members:
    :undoc-members:
```

## See also

- {doc}`index`: the recording workflow and shared recorder options.
- {doc}`plotters`: live plotting instead of writing to a file.
- {doc}`/user_guide/configuration/checkpoints`: checkpoints and trajectories of a scene.
