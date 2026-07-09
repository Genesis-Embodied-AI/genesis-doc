# File writers

A file writer records sampled data to disk. Pass one as the `rec_options` argument of `scene.start_recording`, and the recorder manager samples your data function on schedule and writes each sample to the file. See {doc}`index` for the recording workflow and the shared options (`hz`, `buffer_size`, `save_on_reset`) that every writer inherits.

## `gs.recorders.NPZFile`

Writes samples to a NumPy `.npz` archive. Best for numeric arrays you load back with `numpy.load`.

```{eval-rst}
.. autoclass:: genesis.options.recorders.NPZFile
```

## `gs.recorders.CSVFile`

Writes samples as rows in a `.csv` file. Best for scalar or low-dimensional data you inspect in a spreadsheet.

```{eval-rst}
.. autoclass:: genesis.options.recorders.CSVFile
```

## `gs.recorders.VideoFile`

Encodes a stream of image frames to a video file. Pair it with a data function that returns a rendered frame.

```{eval-rst}
.. autoclass:: genesis.options.recorders.VideoFile
```

## See also

- {doc}`index`: the recording workflow and shared recorder options.
- {doc}`plotters`: live plotting instead of writing to a file.
