# `gs.renderers.BatchRenderer`

A high-throughput renderer that renders many parallel environments together on the GPU, for large-scale data collection and reinforcement-learning observation generation. Enable it with `gs.Scene(renderer=gs.renderers.BatchRenderer(use_rasterizer=True))`; set `use_rasterizer=False` to path-trace instead. It requires the `gs-madrona` package.

With `n_envs > 1`, camera outputs gain a leading batch dimension, for example `rgb` with shape `(n_envs, height, width, 3)`. For installation and a runnable example, see {doc}`/user_guide/rendering/index`.

Unlike the rasterizer, the batch renderer takes its lights at runtime through `scene.add_light(...)` after the scene is created, rather than from `VisOptions`:

```python
scene.add_light(
    pos=(0.0, 0.0, 10.0),   # position, used for positional lights
    dir=(0.0, 0.0, -1.0),   # direction the light travels, normalized internally
    color=(1.0, 1.0, 1.0),  # RGB, each channel in [0, 1]
    intensity=1.0,
    directional=True,       # parallel rays if True, positional if False
    castshadow=True,
    cutoff=45.0,            # spotlight cutoff angle, degrees
    attenuation=0.0,        # distance falloff for positional lights
)
```

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
