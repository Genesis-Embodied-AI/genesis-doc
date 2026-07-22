# BatchRenderer

A high-throughput renderer that renders many parallel environments together on the GPU, for large-scale data collection and reinforcement-learning observation generation. Enable it with `gs.Scene(renderer=gs.renderers.BatchRenderer(use_rasterizer=True))`; set `use_rasterizer=False` to path-trace instead. It requires the `gs-madrona` package.

With `n_envs > 1`, camera outputs gain a leading batch dimension, for example `rgb` with shape `(n_envs, height, width, 3)`. It takes its lights at runtime through `scene.add_light(...)` rather than from `VisOptions`. For installation, lighting, and a runnable example, see {doc}`/user_guide/rendering/index`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.renderers.BatchRenderer
```

## Implementation

```{eval-rst}
.. autoclass:: genesis.vis.batch_renderer.BatchRenderer
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`rasterizer`: the standard single-scene rasterizer
- {doc}`/user_guide/policy_training/examples/index`: rendering observations for RL
