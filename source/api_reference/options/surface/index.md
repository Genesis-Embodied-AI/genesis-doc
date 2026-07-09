# Surface
A `Surface` object encapsulates all visual information used for rendering an entity or its sub-components (links, geoms, etc.)
The surface contains different types textures: diffuse_texture, specular_texture, roughness_texture, metallic_texture, transmission_texture, normal_texture, and emissive_texture. Each one of them is a `gs.textures.Texture` object.

:::{note}
Most advanced surface types are only supported by cameras using the `RayTracer` rendering backend. If `Rasterizer` is used, only color will be rendered.
:::


```{toctree}
:maxdepth: 2

surface
plastic/index
metal/index
emission
glass/index
```
