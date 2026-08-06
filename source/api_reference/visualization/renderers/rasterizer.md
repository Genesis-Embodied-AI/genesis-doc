# Rasterizer

The default renderer: fast, GPU-accelerated rasterization for real-time viewing, control loops, and reinforcement-learning rollouts. It is also the backend the interactive viewer always uses. Name it explicitly with `gs.Scene(renderer=gs.renderers.Rasterizer())`, or omit `renderer` and get it anyway.

The options class takes no parameters. Configure rasterizer behavior such as shadows, lights, and per-environment isolation (`env_separate_rigid`) on `gs.options.VisOptions` rather than on the renderer. See {doc}`/user_guide/rendering/index` for adding cameras and reading back images.

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

- {doc}`raytracer`: photorealistic path tracing.
- {doc}`batch_renderer`: high-throughput parallel rendering.
- {doc}`/api_reference/visualization/lights`: lighting the rasterized scene.
