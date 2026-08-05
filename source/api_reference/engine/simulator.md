# Simulator

The `Simulator` owns the physics solvers and the coupler, and advances them each time you call `scene.step()`. Pass `SimOptions` to the scene as `sim_options` to configure it (timestep, gravity, substeps, differentiable mode), and the scene builds it automatically.

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
