# Options

An options object is a typed group of parameters that configures one component of a scene. You construct the objects you need and pass them to `gs.Scene(...)` and to `scene.add_entity(...)`; anything you omit falls back to its defaults. For the concepts behind these objects and how a setting given in two places is resolved, see {doc}`/user_guide/getting_started/config_system`.

Every class here derives from `gs.options.Options`, a [Pydantic](https://docs.pydantic.dev/) model. Fields are typed and validated on construction, and unknown fields are rejected, so a misspelled or out-of-range argument raises immediately rather than failing later inside a step. You never instantiate `Options` directly; use one of the concrete subclasses below. Many of them, though they live in `gs.options`, are also exposed directly under the `gs` namespace for convenience: `gs.morphs`, `gs.surfaces`, `gs.textures`, and `gs.renderers`.

The classes group into families:

- **Simulator, coupler, and solver options:** `SimOptions` for the simulation as a whole, one options class per physics solver (`RigidOptions`, `MPMOptions`, `SPHOptions`, `FEMOptions`, `SFOptions`, `PBDOptions`, and others), and the coupler that governs how solvers interact (`BaseCouplerOptions` with the `LegacyCouplerOptions`, `SAPCouplerOptions`, and `IPCCouplerOptions` variants). See {doc}`/api_reference/options/simulator_coupler_and_solver_options/index`.
- **Morph options:** the geometry and initial pose of an entity, loaded from primitives, meshes, URDF, MJCF, terrain, or USD. See {doc}`/api_reference/options/morph/index`.
- **Surface options:** how an entity looks when rendered, including its textures. See {doc}`/api_reference/options/surface/index`.
- **Texture options:** the color, image, and batched textures a surface draws from. See {doc}`/api_reference/options/texture/index`.
- **Renderer options:** the rendering backend shared by every camera in a scene — `RendererOptions` and its `Rasterizer`, `RayTracer`, and `BatchRenderer` variants. See {doc}`/api_reference/options/renderer/index`.
- **Viewer and visualization options:** `ViewerOptions` for the interactive viewer and `VisOptions` for viewer-independent visualization. See {doc}`/api_reference/options/vis/index`.
- **Miscellaneous options:** profiling and FPS reporting (`ProfilingOptions`), particle-fluid foam generation (`FoamOptions`), and convex decomposition (`CoacdOptions`). See {doc}`/api_reference/options/misc/index`.

The base class itself is documented in {doc}`/api_reference/options/options`.

```{toctree}
options
simulator_coupler_and_solver_options/index
morph/index
renderer/index
surface/index
texture/index
vis/index
misc/index
```
