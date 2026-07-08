# Surfaces and textures

A **surface** describes how an entity *looks* when rendered: its color, glossiness, transparency, and texture maps. It is separate from the entity's shape and its physics. When you add an entity you pass up to three independent descriptions:

- a {doc}`morph </api_reference/options/morph/index>`: geometry and initial pose,
- a {doc}`material </api_reference/material/index>`: physical behavior (mass, stiffness, friction),
- a {doc}`surface </api_reference/options/surface/index>`: visual appearance, the subject of this page.

Changing a surface never changes how an entity moves or collides; it only changes the rendered image. If you omit the surface, Genesis World uses `gs.surfaces.Default` (a Disney principled BSDF) and honors any material the asset file already defines.

The runnable script that exercises every surface type is [`examples/rendering/demo.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rendering/demo.py):

```python
scene.add_entity(
    morph=gs.morphs.Mesh(file="meshes/sphere.obj", scale=0.5, pos=(0.0, -0.6, 0.0)),
    surface=gs.surfaces.Smooth(color=(0.6, 0.8, 1.0)),
)
```

The rest of this page explains the surface types, how colors and textures are set, and how to light a ray-traced scene.

## Choosing a surface

Every surface is a physically based (PBR) material; the classes differ only in their defaults. Pick the one closest to what you want, then override individual properties.

| Surface | What it is | Notable defaults |
|---|---|---|
| `gs.surfaces.Default` | Disney principled BSDF; the general-purpose surface | alias for `BSDF` |
| `gs.surfaces.Rough` | Matte plastic | `roughness=1.0`, `ior=1.5` |
| `gs.surfaces.Smooth` | Glossy plastic | `roughness=0.1`, `ior=1.5` |
| `gs.surfaces.Reflective` | Near-mirror plastic | `roughness=0.01`, `ior=2.0` |
| `gs.surfaces.Metal` | Conductor with a spectral tint | `metal_type="iron"`, `roughness=0.1` |
| `gs.surfaces.Glass` | Specular reflection and refraction | `roughness=0.0`, `ior=1.5` |
| `gs.surfaces.Water` | Glass tuned for water | `ior=1.2`, `roughness=0.2` |
| `gs.surfaces.Emission` | Emits light; used as a light source | — |

`Iron`, `Gold`, `Copper`, and `Aluminium` are shortcuts for `Metal` with the matching `metal_type`. The full set of `metal_type` values is `"aluminium"`, `"gold"`, `"copper"`, `"brass"`, `"iron"`, `"titanium"`, `"vanadium"`, and `"lithium"`, each carrying its own index of refraction.

```python
# both spheres are gold; the second spells out what the shortcut sets
scene.add_entity(morph=gold_sphere, surface=gs.surfaces.Gold())
scene.add_entity(morph=gold_sphere, surface=gs.surfaces.Metal(metal_type="gold"))
```

## Setting color and PBR properties

Each PBR channel is really a *texture* (see below), but when a channel is a single constant you set it with a shortcut argument instead of building a texture object. The common shortcuts are `color`, `roughness`, `opacity`, `emissive`, `metallic`, and `ior`:

```python
surface = gs.surfaces.Default(
    color=(0.8, 0.2, 0.2),  # base (diffuse) color, RGB in [0, 1]
    roughness=0.4,          # 0 = mirror-smooth, 1 = fully matte
    metallic=0.0,           # 0 = dielectric, 1 = metal
)
```

Two constraints follow from how the shortcuts map onto channels:

- A shortcut and its texture cannot both be set. Passing `color=...` together with `diffuse_texture=...` raises an error. The texture already carries the color.
- A shortcut only applies to channels the surface actually has. `metallic` is meaningful on `Default`/`BSDF`; `Metal`, `Glass`, and the plastics ignore it because their reflectance is fixed by their type.

A fourth color component is treated as opacity, so `color=(r, g, b, a)` is the concise way to make a surface semi-transparent:

```python
# 50% transparent glossy plastic
gs.surfaces.Smooth(color=(1.0, 1.0, 1.0, 0.5))
```

## Textures

When a property varies across a surface — a wood grain, a painted logo, a roughness map — supply a texture instead of a constant. Textures live under `gs.textures`:

- `gs.textures.ColorTexture(color=...)`: a single uniform color. Equivalent to the `color` shortcut, useful when an argument requires a texture object.
- `gs.textures.ImageTexture(image_path=..., encoding=...)`: an image map sampled over the mesh's UV coordinates.
- `gs.textures.BatchTexture`: a stack of textures, one per environment, for {doc}`parallel rendering <parallel_simulation>`.

Assign a texture to the channel it drives. The base color goes to `diffuse_texture`; data maps go to `roughness_texture`, `normal_texture`, `opacity_texture`, and so on:

```python
surface = gs.surfaces.Rough(
    diffuse_texture=gs.textures.ImageTexture(image_path="textures/checker.png"),
    roughness_texture=gs.textures.ImageTexture(image_path="rough.png", encoding="linear"),
    normal_texture=gs.textures.ImageTexture(image_path="normal.png", encoding="linear"),
)
```

:::{warning}
Set `encoding="linear"` for any map that stores data rather than a color: roughness, metallic, normal, and opacity maps. The default `encoding="srgb"` applies gamma correction that is correct for color images but corrupts data maps. `.hdr` and `.exr` files are forced to `linear` automatically.
:::

An image path is resolved against your working directory first, then against the bundled asset directory (`genesis/assets`), so `"textures/checker.png"` loads the checker image that ships with Genesis World. A loaded asset (a `.glb` or textured `.obj`, for example) brings its own surface; pass a `surface` to `add_entity` only when you want to override it.

## Lighting a ray-traced scene

In the {doc}`Nyx <nyx_renderer>` ray tracer, lights are not a special object: they are ordinary entities with an `Emission` surface. An environment map is the same idea applied to the background: an emissive image wrapped around the scene provides ambient illumination.

This excerpt from `examples/rendering/demo.py` sets an HDRI-style environment map and one area light:

```python
scene = gs.Scene(
    renderer=gs.renderers.RayTracer(
        env_surface=gs.surfaces.Emission(
            emissive_texture=gs.textures.ImageTexture(image_path="textures/indoor_bright.png"),
        ),
        env_radius=15.0,          # meters; the environment sphere's radius
        env_euler=(0, 0, 180),    # extrinsic x-y-z, degrees; rotates the map
        lights=[
            {"pos": (0.0, 0.0, 10.0), "radius": 3.0, "color": (15.0, 15.0, 15.0)},
        ],
    ),
)
```

:::{note}
Surfaces render on both the interactive viewer's rasterizer and the ray tracer, but reflections, refraction, transmission, and emission-based lighting are only fully resolved by the ray tracer. See {doc}`Visualization <visualization>` for how to choose and configure a renderer.
:::

## Visualizing something other than the visual mesh

`vis_mode` selects *which* geometry of an entity is drawn, independent of the surface's material. It is most useful for particle-based entities, whose "shape" is a point cloud rather than a mesh:

```python
# draw a fluid entity as its raw particles
gs.surfaces.Rough(color=(0.6, 0.8, 1.0), vis_mode="particle")

# reconstruct a smooth surface mesh from those particles
gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7), vis_mode="recon")
```

The accepted values are `"visual"`, `"collision"`, `"particle"`, `"sdf"`, and `"recon"`. Use `"collision"` to inspect the collision geometry that physics actually sees.

## Next steps

- {doc}`Visualization <visualization>`: cameras, the viewer, and choosing a renderer.
- {doc}`Nyx renderer <nyx_renderer>`: the ray tracer and its options in depth.
- {doc}`USD import <usd_import>`: loading assets that carry their own surfaces.
