# BSDF

`gs.surfaces.BSDF` is a Disney principled BSDF surface, carrying the full set of physically based rendering (PBR) parameters. `gs.surfaces.Default` subclasses it and adds no parameters of its own, so the PBR controls documented here, such as `specular_trans`, `diffuse_trans`, and `metallic_texture`, apply to both.

```{eval-rst}
.. autoclass:: genesis.options.surfaces.BSDF
```
