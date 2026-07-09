# Renderers

A renderer is the backend that camera sensors use to turn a scene into images. Select one per scene by passing an instance to `gs.Scene(renderer=...)`; the choice applies to every camera sensor and does not affect the interactive viewer, which always rasterizes. For the task-oriented walkthrough, see {doc}`/user_guide/rendering/index`.

| Renderer | Speed | Quality | Use it for |
|---|---|---|---|
| {doc}`Rasterizer <rasterizer>` | Fast | Good | real-time viewing, control loops, RL rollouts (the default) |
| {doc}`RayTracer <raytracer>` | Slow | Photorealistic | high-quality stills (Luisa backend, deprecating in favor of Nyx) |
| {doc}`BatchRenderer <batch_renderer>` | Very fast | Good | rendering many parallel environments on the GPU |

Every renderer options class derives from `RendererOptions`:

```{eval-rst}
.. autoclass:: genesis.options.renderers.RendererOptions
```

```{toctree}
:titlesonly:
:hidden:

rasterizer
raytracer
batch_renderer
```

## See also

- {doc}`/user_guide/rendering/index`: adding cameras, image types, video, and backends
- {doc}`/api_reference/visualization/lights`: lighting a rendered scene
