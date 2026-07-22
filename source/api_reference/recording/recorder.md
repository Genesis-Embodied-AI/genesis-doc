# Recorder

The base class for all recorders: it captures and processes sampled simulation data over a build/process/cleanup/reset lifecycle. Subclass it to record data in a custom way; see {doc}`/user_guide/developers/extending_genesis`.

```{eval-rst}
.. autoclass:: genesis.recorders.base_recorder.Recorder
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/developers/extending_genesis`: writing a custom recorder.
- {doc}`recorder_manager`: the per-scene coordinator that drives recorders.
- {doc}`file_writers` and {doc}`plotters`: the built-in recorders.
