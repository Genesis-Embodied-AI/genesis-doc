# Surfaces and textures

A **surface** describes how an entity *looks* when rendered: its color, glossiness, transparency, and texture maps. Every entity takes up to three independent descriptions:

- a {doc}`morph </api_reference/engine/entity/morph/index>`: geometry and initial pose,
- a {doc}`material </api_reference/engine/material/index>`: physical behavior (mass, stiffness, friction),
- a {doc}`surface </api_reference/engine/entity/surface/index>`: visual appearance, the subject of this page.

Changing a surface never changes how an entity moves or collides; it only changes the rendered image. If you omit the surface, Genesis World uses {py:class}`gs.surfaces.Default <genesis.options.surfaces.Default>` (a Disney principled BSDF) and honors any material the asset file already defines.

The runnable script that exercises every surface type is [`examples/rendering/demo.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rendering/demo.py):

```python
scene.add_entity(
    morph=gs.morphs.Mesh(file="meshes/sphere.obj", scale=0.5, pos=(0.0, -0.6, 0.0)),
    surface=gs.surfaces.Smooth(color=(0.6, 0.8, 1.0)),
)
```

## Choosing a surface

Every surface is a physically based (PBR) material; the classes differ only in their defaults. Pick the one closest to what you want, then override individual properties.

| Surface | What it is | Notable defaults |
|---|---|---|
| `gs.surfaces.Default` | Disney principled BSDF; the general-purpose surface | alias for {py:class}`BSDF <genesis.options.surfaces.BSDF>` |
| {py:class}`gs.surfaces.Rough <genesis.options.surfaces.Rough>` | Matte plastic | `roughness=1.0`, `ior=1.5` |
| {py:class}`gs.surfaces.Smooth <genesis.options.surfaces.Smooth>` | Glossy plastic | `roughness=0.1`, `ior=1.5` |
| {py:class}`gs.surfaces.Reflective <genesis.options.surfaces.Reflective>` | Near-mirror plastic | `roughness=0.01`, `ior=2.0` |
| {py:class}`gs.surfaces.Metal <genesis.options.surfaces.Metal>` | Conductor with a spectral tint | `metal_type="iron"`, `roughness=0.1` |
| {py:class}`gs.surfaces.Glass <genesis.options.surfaces.Glass>` | Specular reflection and refraction | `roughness=0.0`, `ior=1.5` |
| {py:class}`gs.surfaces.Water <genesis.options.surfaces.Water>` | Glass tuned for water | `ior=1.2`, `roughness=0.2` |
| {py:class}`gs.surfaces.Emission <genesis.options.surfaces.Emission>` | Emits light; used as a light source | — |

{py:class}`Iron <genesis.options.surfaces.Iron>`, {py:class}`Gold <genesis.options.surfaces.Gold>`, {py:class}`Copper <genesis.options.surfaces.Copper>`, and {py:class}`Aluminium <genesis.options.surfaces.Aluminium>` are shortcuts for `Metal` with the matching `metal_type`. The full set of `metal_type` values is `"aluminium"`, `"gold"`, `"copper"`, `"brass"`, `"iron"`, `"titanium"`, `"vanadium"`, and `"lithium"`, each carrying its own index of refraction.

```python
# both spheres are gold; the second spells out what the shortcut sets
scene.add_entity(morph=gold_sphere, surface=gs.surfaces.Gold())
scene.add_entity(morph=gold_sphere, surface=gs.surfaces.Metal(metal_type="gold"))
```

## Setting color and PBR properties

Each PBR channel is really a *texture* (see below), but a channel that holds a single constant takes a shortcut argument instead of a texture object. The common shortcuts are `color`, `roughness`, `opacity`, `emissive`, `metallic`, and `ior`:

```python
surface = gs.surfaces.Default(
    color=(0.8, 0.2, 0.2),  # base (diffuse) color, RGB in [0, 1]
    roughness=0.4,          # 0 = mirror-smooth, 1 = fully matte
    metallic=0.0,           # 0 = dielectric, 1 = metal
)
```

Two constraints follow from how the shortcuts map onto channels:

- A shortcut and its texture cannot both be set: passing `color=...` together with the texture it fills (`diffuse_texture` on most surfaces, `specular_texture` on `Glass` and `Water`, `emissive_texture` on `Emission`) raises an error, because the texture already carries the color.
- A shortcut only applies to channels the surface actually has. `metallic` is meaningful on `Default`/`BSDF`; `Metal`, `Glass`, and the plastics ignore it because their reflectance is fixed by their type.

Genesis World treats a fourth color component as opacity, so `color=(r, g, b, a)` is the concise way to make a surface semi-transparent:

```python
# 50% transparent glossy plastic
gs.surfaces.Smooth(color=(1.0, 1.0, 1.0, 0.5))
```

## Textures

When a property varies across a surface (a wood grain, a painted logo, a roughness map), supply a texture instead of a constant. Textures live under `gs.textures`:

- `gs.textures.ColorTexture(color=...)`: a single uniform color. Equivalent to the `color` shortcut, useful when an argument requires a texture object.
- `gs.textures.ImageTexture(image_path=..., encoding=...)`: an image map sampled over the mesh's UV coordinates.
- {py:class}`gs.textures.BatchTexture <genesis.options.textures.BatchTexture>`: a stack of textures, one per environment, for {doc}`parallel rendering </user_guide/getting_started/parallel_simulation>`.
- {py:class}`gs.textures.DynamicTexture <genesis.options.textures.DynamicTexture>`: an image that changes while the simulation runs (see [Changing a texture at runtime](#changing-a-texture-at-runtime)).

Assign a texture to the channel it drives. The base color goes to `diffuse_texture`; data maps go to `roughness_texture`, `normal_texture`, `opacity_texture`, and so on:

```python
surface = gs.surfaces.Default(
    diffuse_texture=gs.textures.ImageTexture(image_path="textures/checker.png"),
    roughness_texture=gs.textures.ImageTexture(image_path="rough.png", encoding="linear"),
    normal_texture=gs.textures.ImageTexture(image_path="normal.png", encoding="linear"),
)
```

:::{warning}
Set `encoding="linear"` for any map that stores data rather than a color: roughness, metallic, normal, and opacity maps. The default `encoding="srgb"` applies gamma correction that is correct for color images but corrupts data maps. `.hdr` and `.exr` files must be loaded with `encoding="linear"`; any other encoding raises an error.
:::

Genesis World resolves an image path against your working directory first, then against the bundled asset directory (`genesis/assets`), so `"textures/checker.png"` loads the checker image that ships with the library. A loaded asset (a `.glb` or textured `.obj`, for example) brings its own surface; pass a `surface` to `add_entity` only when you want to override it.

### Changing a texture at runtime

A `DynamicTexture` fills the diffuse or the emissive map with an image that changes while the simulation runs, such as a screen or an indicator light. Declare the `resolution` of its images and its `variants`, the images each environment switches between, then show one per environment after the build with `set_texture(variant=...)`. With `is_batched=True`, each environment also holds an image of its own, which `set_texture(pixels)` writes. The full script is [`examples/rendering/dynamic_texture.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rendering/dynamic_texture.py):

```python
duck = scene.add_entity(
    gs.morphs.Mesh(file="meshes/duck/duck.obj", scale=0.0005, euler=(90.0, 0.0, 90.0), fixed=True),
    surface=gs.surfaces.Default(
        diffuse_texture=gs.textures.DynamicTexture(
            resolution=(256, 256),  # (width, height), pixels
            variants={
                "asset": None,  # the texture the asset gives the map
                "purple": gs.textures.ColorTexture(color=(0.71, 0.62, 0.86)),
            },
            is_batched=True,
        ),
    ),
)
scene.build(n_envs=2)

duck.set_texture(variant="purple")  # every environment
duck.set_texture(variant=["asset", "purple"])  # one variant per environment
duck.set_texture(np.random.rand(2, 3))  # one RGB color per environment, written to the batched variant
```

Every environment shows the first variant at build and after a reset. The mesh needs texture coordinates, and only the rasterizer draws a dynamic texture. Rigid, kinematic, and FEM entities take one, and so do PBD cloth and elastic entities.

## Lighting a ray-traced scene

In the Luisa ray tracer (`gs.renderers.RayTracer`), lights are emissive geometry: the sphere lights listed in `RayTracer(lights=...)`, meshes added with `scene.add_mesh_light(...)`, and any entity with an `Emission` surface. An environment map is the same idea applied to the background: an emissive image wrapped around the scene lights everything in it.

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
Surfaces render on both the interactive viewer's rasterizer and the ray tracer, but reflections, refraction, transmission, and emission-based lighting are only fully resolved by the ray tracer. See {doc}`Rendering </user_guide/rendering/cameras>` for how to choose and configure a renderer.
:::

## Geometry a surface is drawn on

The material of an entity decides which geometry its surface is drawn on. Rigid, kinematic, and FEM entities, PBD cloth and elastic entities, and MPM solids draw their visual mesh, moved or deformed to follow the simulation. A liquid or granular material (SPH, MPM liquid, sand, and snow, PBD liquid and particles) draws a surface reconstructed from its particles, and so does an MPM solid in an environment where it tears. To see the collision geometry, the particles, or the tetrahedra instead, switch to the {ref}`debug view <debug-view>`, which leaves the surface as it is.

## Foam and spray

A fast-moving particle fluid entrains air: whitewater on a breaking wave, spray thrown off a splash, bubbles carried below the surface. Genesis World renders these as secondary foam particles around a particle-based fluid in the ray tracer. The foam is a rendering effect, so it leaves the physics untouched and the rasterizer ignores it.

Enable it on the fluid's surface with `generate_foam=True`, and tune the look with a `foam_options` object:

```python
scene.add_entity(
    material=gs.materials.SPH.Liquid(),
    morph=gs.morphs.Box(pos=(0.0, 0.0, 0.5), size=(0.4, 0.4, 0.4)),
    surface=gs.surfaces.Water(
        generate_foam=True,
        foam_options=gs.options.FoamOptions(
            radius_scale=0.2,  # foam particle radius relative to a fluid particle
            k_foam=1000.0,  # foam particles generated per frame
            spray_decay=2.0,
            foam_decay=1.0,
            bubble_decay=5.0,
        ),
    ),
)
```

{py:class}`gs.options.FoamOptions <genesis.options.misc.FoamOptions>` splits the effect into three populations, each with its own dissipation rate (a larger value clears that population faster):

- **`radius_scale`:** foam particle radius as a fraction of the fluid particle radius. Defaults to `0.2`.
- **`k_foam`:** number of foam particles generated per frame. Defaults to `1000.0`.
- **`spray_decay`:** dissipation rate of airborne spray. Defaults to `2.0`.
- **`foam_decay`:** dissipation rate of foam riding the surface. Defaults to `1.0`.
- **`bubble_decay`:** dissipation rate of submerged bubbles. Defaults to `5.0`.
- **`color`:** RGBA tint of the foam particles. Defaults to `(0.7, 0.7, 0.7, 0.7)`.

## See also

- {doc}`Rendering </user_guide/rendering/cameras>`: cameras and choosing a renderer.
- {doc}`Nyx renderer <nyx_renderer>`: photorealistic path tracing in depth.
- {doc}`USD import </user_guide/assets/usd_import>`: loading assets that carry their own surfaces.
