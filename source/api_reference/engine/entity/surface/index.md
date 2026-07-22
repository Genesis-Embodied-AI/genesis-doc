# Surface

A `Surface` object encapsulates all visual information used for rendering an entity or its sub-components (links, geoms, etc.)
The surface contains different types textures: diffuse_texture, specular_texture, roughness_texture, metallic_texture, transmission_texture, normal_texture, and emissive_texture. Each one of them is a `gs.textures.Texture` object. For which surface properties render under each backend, see {doc}`/user_guide/rendering/surfaces_textures`.

```{toctree}
:maxdepth: 2
:titlesonly:

surface
plastic/index
metal/index
emission
glass/index
foam_options
```
