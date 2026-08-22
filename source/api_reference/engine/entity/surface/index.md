# Surface

A surface holds the visual information the renderer uses for an entity, or for its individual links and geoms. A surface carries a texture per channel: `diffuse_texture`, `specular_texture`, `roughness_texture`, `metallic_texture`, `transmission_texture`, `normal_texture`, and `emissive_texture`, each a {doc}`gs.textures.Texture </api_reference/engine/entity/texture/index>` object. For which surface properties render under each backend, see {doc}`/user_guide/rendering/surfaces_textures`.

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
