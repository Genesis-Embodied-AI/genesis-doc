# Loading Assets

Almost everything you put in a scene comes from an asset file loaded through a **morph**: the object that pairs an entity's geometry with its initial pose and scale, and that you pass as the first argument to `scene.add_entity(...)`. This section covers getting external geometry into Genesis World correctly, from the supported file formats to the mesh preparation that makes a model simulate well. Start with the general loading workflow, which applies to every format.

```{toctree}
:hidden:
:maxdepth: 1

loading_assets
usd_import
mesh_processing
```
