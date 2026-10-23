# Options system

Genesis World is configured through **options objects**: small, typed parameter groups under `gs.options.*` that you pass to `gs.Scene(...)` and to `scene.add_entity(...)`. Rather than have a scene accept dozens of loose keyword arguments, we give each concern its own object with its own defaults: one for the global simulator, one per physics solver, one for the viewer, and one per renderer. This page explains what those objects are, how they compose into a scene, and how we resolve a setting given in two places.

If you have not built a scene yet, read {doc}`/user_guide/getting_started/hello_genesis` first. It uses {py:class}`SimOptions <genesis.options.solvers.SimOptions>` and {py:class}`ViewerOptions <genesis.options.ViewerOptions>` in passing. This page is the conceptual reference behind that usage.

## Composing a scene from options

Every configurable component of a scene is described by one options object. Construct the objects you care about and hand them to the scene; anything you omit uses its defaults.

```python
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, gravity=(0, 0, -9.81)),
    rigid_options=gs.options.RigidOptions(enable_collision=True),
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    show_viewer=True,
)
```

The options split into three roles, plus a set of per-entity options passed to `add_entity` rather than to the scene:

- **Global.** `SimOptions` sets the properties of the simulation as a whole, and the coupler options set how solvers interact.
- **Per solver.** One options object per physics solver (rigid, MPM, SPH, FEM, SF, PBD), each configuring that solver alone.
- **Visualization.** The viewer, the solver-independent visualization, and the renderer.

## Every options object shares one base

All `gs.options.*` classes derive from {py:class}`gs.options.Options <genesis.options.options.Options>`, a [Pydantic](https://docs.pydantic.dev/) model. Two properties of that base matter in practice:

- **Fields are typed and validated on construction.** A value of the wrong type, or out of range, raises immediately with a readable message, not deep inside the first `scene.step()`.
- **Unknown fields are rejected.** The base sets `extra="forbid"`, so a misspelled argument such as `gravty=(0, 0, -9.81)` raises `Unrecognized attribute 'gravty'` instead of being silently ignored.

You never instantiate `Options` directly; you always use a concrete subclass. Each option class is documented in the {doc}`API Reference </api_reference/index>` alongside the component it configures.

## Solver options override simulator options

`SimOptions` holds settings that are global by default: most importantly the timestep `dt` (seconds) and `gravity` (m/s², pointing down `-Z`). Each solver also exposes those same settings on its own options object, where they default to `None`.

A value set on a solver's options overrides the global `SimOptions` value, for that solver only, and a solver whose field is left at `None` inherits the global value.

`SimOptions.dt` is how much simulated time one `scene.step()` advances. A solver's `dt` is the interval it integrates over, so it must divide the step a whole number of times, and that quotient is the number of substeps per step. Every active solver advances together, so the count one solver asks for is the count they all take, and two solvers asking for different intervals raise. `SimOptions.substeps` requests the same count directly, and setting both raises unless they agree.

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),        # one step advances 0.01 s
    rigid_options=gs.options.RigidOptions(dt=0.005),   # two substeps per step, for every solver
    # mpm_options left unset -> the MPM solver, if used, integrates twice per step as well, over 0.005 s
)
```

The same inheritance applies to `gravity`, and each solver keeps its own value, so read it back from the solver simulating the entity, for example `scene.rigid_solver.get_gravity(envs_idx)`. A scene coupling its solvers through IPC applies the `SimOptions` gravity to every body it couples, so a coupled solver authoring a different one raises at build time. Settings that are meaningful only to one solver (for example `RigidOptions.constraint_solver` or `RigidOptions.max_collision_pairs`) live solely on that solver's options and have no global counterpart.

## Scene-level option groups

Each of these is an optional argument to `gs.Scene(...)`.

| Options class | `Scene` argument | Configures |
|---|---|---|
| {py:class}`gs.options.SimOptions <genesis.options.solvers.SimOptions>` | `sim_options` | Global timestep, gravity, substeps, differentiable mode. |
| {py:class}`gs.options.BaseCouplerOptions <genesis.options.solvers.BaseCouplerOptions>` | `coupler_options` | Coupling between solvers. Concrete variants: {py:class}`LegacyCouplerOptions <genesis.options.solvers.LegacyCouplerOptions>`, {py:class}`SAPCouplerOptions <genesis.options.solvers.SAPCouplerOptions>`, {py:class}`IPCCouplerOptions <genesis.options.solvers.IPCCouplerOptions>`. |
| {py:class}`gs.options.RigidOptions <genesis.options.solvers.RigidOptions>` | `rigid_options` | Rigid-body dynamics: contact, collision, constraints, integrator. |
| {py:class}`gs.options.MPMOptions <genesis.options.solvers.MPMOptions>` | `mpm_options` | Material Point Method solver (elastic, plastic, granular, fluid). |
| {py:class}`gs.options.SPHOptions <genesis.options.solvers.SPHOptions>` | `sph_options` | Smoothed Particle Hydrodynamics solver (fluids, granular flow). |
| {py:class}`gs.options.FEMOptions <genesis.options.solvers.FEMOptions>` | `fem_options` | Finite Element Method solver (elastic material). |
| {py:class}`gs.options.SFOptions <genesis.options.solvers.SFOptions>` | `sf_options` | Stable Fluid solver (Eulerian gaseous simulation). |
| {py:class}`gs.options.PBDOptions <genesis.options.solvers.PBDOptions>` | `pbd_options` | Position-Based Dynamics solver (cloth, deformables, liquids, particles). |
| {py:class}`gs.options.KinematicOptions <genesis.options.solvers.KinematicOptions>` | `kinematic_options` | Kinematic (non-dynamic) entities. |
| {py:class}`gs.options.ToolOptions <genesis.options.solvers.ToolOptions>` | `tool_options` | Legacy tool solver. Slated for deprecation. |
| {py:class}`gs.options.VisOptions <genesis.options.VisOptions>` | `vis_options` | Visualization independent of any viewer or camera. |
| {py:class}`gs.options.ViewerOptions <genesis.options.ViewerOptions>` | `viewer_options` | The interactive viewer: camera pose, resolution, refresh rate. |
| {py:class}`gs.options.ProfilingOptions <genesis.options.profiling.ProfilingOptions>` | `profiling_options` | Timing and FPS reporting. |
| {py:class}`gs.renderers.RendererOptions <genesis.options.renderers.RendererOptions>` | `renderer` | Rendering backend: `Rasterizer`, `RayTracer`, or `BatchRenderer`. |

The solver and coupler options are documented beside their solver and coupler in the {doc}`physics engine reference </api_reference/engine/index>`, the global `SimOptions` under {doc}`Scene </api_reference/engine/index>`, and the viewer, visualization, and renderer options in the {doc}`visualization reference </api_reference/visualization/index>`.

:::{note}
Not every solver runs in every scene. A solver is active only once you add an entity whose material targets it: adding a rigid entity activates the rigid solver, and so on. Options for an inactive solver are simply unused.
:::

## Per-entity options

`add_entity` takes its own options describing a single entity rather than the scene:

```python
franka = scene.add_entity(
    morph=gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default(),
)
```

- **Morph:** the entity's geometry and initial pose. See {doc}`/user_guide/getting_started/hello_genesis` for loading morphs and the {doc}`morph API </api_reference/engine/entity/morph/index>`.
- **Material:** how the entity responds to physical forces, and which solver simulates it. See {doc}`/user_guide/physics/beyond_rigid_bodies`.
- **Surface:** how the entity looks when rendered. See {doc}`/user_guide/rendering/surfaces_textures`.

## See also

- {doc}`/user_guide/getting_started/hello_genesis`: the minimal scene that uses these options.
- {doc}`/user_guide/interaction/visualization`: the interactive viewer and command-line tools.
- {doc}`/user_guide/rendering/cameras`: cameras, image types, video, and rendering backends.
- {doc}`API Reference </api_reference/index>`: each option class, documented with the component it configures.
