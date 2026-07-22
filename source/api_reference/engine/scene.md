# Scene

The `Scene` is the top-level container for a simulation: you add entities to it, build it, and step it. It is assembled from a bundle of options passed to `gs.Scene(...)`, each documented with the component it configures: `sim_options` (the {doc}`Simulator <simulator>`), the per-solver options (with each {doc}`solver <solvers/index>`), `coupler_options` (the {doc}`coupler <couplers/index>`), `viewer_options` and `vis_options` (the {doc}`viewer </api_reference/visualization/viewer>`), `renderer` (the {doc}`renderer </api_reference/visualization/renderers/index>`), and `profiling_options` below. For a worked example, see {doc}`/user_guide/getting_started/hello_genesis`.

```{eval-rst}
.. autoclass:: genesis.engine.scene.Scene
    :members:
    :undoc-members:
    :show-inheritance:
```

## Profiling options

```{eval-rst}
.. autoclass:: genesis.options.profiling.ProfilingOptions
```
