# Simulator

The `Simulator` owns the physics solvers and the coupler, and advances them each time you call `scene.step()`. It is configured by `SimOptions` (timestep, gravity, substeps, differentiable mode), passed to the scene as `sim_options`, and the scene builds it automatically.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.SimOptions
```

## Simulator

```{eval-rst}
.. autoclass:: genesis.engine.simulator.Simulator
    :members:
    :undoc-members:
    :show-inheritance:
```
