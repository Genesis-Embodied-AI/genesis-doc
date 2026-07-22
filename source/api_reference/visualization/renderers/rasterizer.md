# Rasterizer

The default renderer: fast, GPU-accelerated rasterization for real-time viewing, control loops, and reinforcement-learning rollouts. It is also the backend the interactive viewer always uses. Enable it explicitly with `gs.Scene(renderer=gs.renderers.Rasterizer())`, though it is already the default when `renderer` is omitted.

The options class takes no parameters. Rasterizer behavior such as shadows, lights, and per-environment isolation (`env_separate_rigid`) is configured on `gs.options.VisOptions`, not on the renderer. See {doc}`/user_guide/rendering/index` for adding cameras and reading back images.

## Options

```{eval-rst}
.. autoclass:: genesis.options.renderers.Rasterizer
```

## Implementation

```{eval-rst}
.. autoclass:: genesis.vis.rasterizer.Rasterizer
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`raytracer`: photorealistic path tracing
- {doc}`batch_renderer`: high-throughput parallel rendering
- {doc}`/api_reference/visualization/lights`: lighting the rasterized scene
