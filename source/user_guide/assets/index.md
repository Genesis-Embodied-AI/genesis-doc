# Loading Assets

Almost everything you put in a scene, a robot, a rigid object, a static prop, comes from an asset file loaded through a **morph**: the object that pairs an entity's geometry with its initial pose and scale, and that you pass as the first argument to `scene.add_entity(...)`. This section covers getting external geometry into Genesis World correctly, from the file formats it accepts to the preparation a mesh needs before it simulates well.

Begin with the general loading workflow, which applies to every format, then read the format- and task-specific pages as you need them: importing a full USD scene, or processing a raw mesh into the separate visual and collision representations the engine expects.

- {doc}`loading_assets` is the foundation: the supported morph types and file formats, the pose and scale options common to all of them, and how Genesis World resolves asset paths.
- {doc}`usd_import` covers importing [Universal Scene Description](https://openusd.org/) files, including the physics properties Genesis World reads from a USD stage.
- {doc}`mesh_processing` explains the two jobs a mesh must do, looking right as a visual mesh and behaving well as a collision mesh, and the processing (convex decomposition, simplification) that reconciles them.

```{toctree}
:hidden:
:maxdepth: 1

loading_assets
usd_import
mesh_processing
```
