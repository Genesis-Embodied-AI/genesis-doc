# Lights

Lights illuminate a rendered scene. How you add them depends on the backend:

- **Rasterizer (and the viewer):** lights come from the `lights` list on `gs.options.VisOptions`, using the light classes in `gs.options.vis`. With no configuration the scene gets a single directional light, so it is lit out of the box. Ambient fill is set separately through `VisOptions.ambient_light`.
- **RayTracer:** there are no light objects. Lights are entities with an `Emission` {doc}`surface </api_reference/options/surface/emission>`, plus optional `SphereLight` area lights (below).
- **BatchRenderer:** lights are added at runtime with `scene.add_light(...)`; see {doc}`renderers/batch_renderer`.

```python
scene = gs.Scene(
    vis_options=gs.options.VisOptions(
        lights=[
            gs.options.vis.DirectionalLight(
                dir=(-1, -1, -1),       # direction the light travels, world frame
                color=(1.0, 1.0, 1.0),  # RGB in [0, 1]
                intensity=5.0,
            ),
            gs.options.vis.PointLight(
                pos=(2.0, 0.0, 3.0),    # meters, world frame
                color=(1.0, 0.9, 0.8),
                intensity=8.0,
            ),
        ],
        ambient_light=(0.1, 0.1, 0.1),  # uniform fill so shadows are not pure black
    ),
)
```

For the task-oriented explanation, see {doc}`/user_guide/rendering/index`.

## Rasterizer lights

These classes populate the `lights` list on `gs.options.VisOptions` and light the rasterizer and the viewer.

### `gs.options.vis.DirectionalLight`

A light with parallel rays and no position, like the sun. The scene's default light is one of these.

```{eval-rst}
.. autoclass:: genesis.options.vis.DirectionalLight
```

### `gs.options.vis.PointLight`

A light that emits from a point in space, falling off with distance.

```{eval-rst}
.. autoclass:: genesis.options.vis.PointLight
```

### `gs.options.vis.AmbientLight`

A uniform fill light with no direction, applied everywhere so shadows are not pure black. Ambient fill can also be set directly through `VisOptions.ambient_light`.

```{eval-rst}
.. autoclass:: genesis.options.vis.AmbientLight
```

## SphereLight

A spherical area light for the `RayTracer` renderer. Add one or more to a scene to illuminate it, controlling position, color, intensity, and radius. Color values are not restricted to `[0, 1]`, so they can express HDR intensities.

```{eval-rst}
.. autoclass:: genesis.options.renderers.SphereLight
```

## See also

- {doc}`viewer`: `VisOptions`, which holds the rasterizer light list
- {doc}`renderers/raytracer`: photorealistic rendering
- {doc}`/api_reference/options/surface/emission`: emissive surfaces
