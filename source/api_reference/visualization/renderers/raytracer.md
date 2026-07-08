# `gs.renderers.RayTracer`

A path-tracing renderer backed by LuisaRender, for photorealistic stills with global illumination, reflections, and refractions. Enable it with `gs.Scene(renderer=gs.renderers.RayTracer(...))`. Per-camera ray-tracing settings such as `spp` (samples per pixel), `denoise`, `model` (`"pinhole"` or `"thinlens"`), `aperture`, and `focus_dist` are passed to `scene.add_camera()`, not to the renderer.

Photorealistic output depends on entity {doc}`surfaces </api_reference/options/surface/index>` (metal, glass, plastic, emission) and on scene {doc}`lighting </api_reference/visualization/lights>`. For setup and a worked example, see {doc}`/user_guide/rendering/index`.

:::{warning}
This backend is deprecated in favor of {doc}`Nyx </user_guide/rendering/nyx_renderer>` and must be built from source (the LuisaRender extra). Prefer Nyx for new work.
:::

## Options

```{eval-rst}
.. autoclass:: genesis.options.renderers.RayTracer
```

The underlying `genesis.vis.raytracer.Raytracer` implementation is importable only when the optional ray-tracing extra is installed, so it is not auto-documented here.

## See also

- {doc}`rasterizer`: the fast default renderer
- {doc}`/user_guide/rendering/nyx_renderer`: the recommended photorealistic path
- {doc}`/api_reference/options/surface/index`: surface materials for ray tracing
