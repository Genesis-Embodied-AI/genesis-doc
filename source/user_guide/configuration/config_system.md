# Options system

Genesis World is configured through **options objects**: small, typed parameter groups under `gs.options.*` that you pass to `gs.Scene(...)` and to `scene.add_entity(...)`. Rather than a scene taking dozens of loose keyword arguments, each concern (the global simulator, one physics solver, the viewer, a renderer) gets its own object with its own defaults. This page explains what those objects are, how they compose into a scene, and how a setting given in two places is resolved.

If you have not built a scene yet, read {doc}`/user_guide/getting_started/hello_genesis` first. It uses `SimOptions` and `ViewerOptions` in passing. This page is the conceptual reference behind that usage.

## A scene is assembled from options

Every configurable component of a scene is described by one options object. You construct the objects you care about and hand them to the scene; anything you omit uses its defaults.

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

- **Global.** `SimOptions` sets the properties of the simulation as a whole; coupler options set how solvers interact.
- **Per solver.** One options object per physics solver (rigid, MPM, SPH, FEM, SF, PBD), each configuring that solver alone.
- **Visualization.** The viewer, solver-independent visualization, and the renderer.

## Every options object shares one base

All `gs.options.*` classes derive from `gs.options.Options`, a [Pydantic](https://docs.pydantic.dev/) model. Two properties of that base matter in practice:

- **Fields are typed and validated on construction.** A value of the wrong type, or out of range, raises immediately with a readable message, not deep inside the first `scene.step()`.
- **Unknown fields are rejected.** The base sets `extra="forbid"`, so a misspelled argument such as `gravty=(0, 0, -9.81)` raises `Unrecognized attribute 'gravty'` instead of being silently ignored.

You never instantiate `Options` directly; you always use a concrete subclass. See the {doc}`Options API </api_reference/options/index>` for the full class list.

## Simulator options override solver options

`SimOptions` holds settings that are global by default: most importantly the timestep `dt` (seconds) and `gravity` (N/kg, pointing down `-Z`). Each solver also exposes those same settings on its own options object, where they default to `None`.

The rule is: **a value set on a solver's options overrides the global `SimOptions` value, for that solver only.** A solver whose field is left at `None` inherits the global value. This lets most scenes set `dt` once while allowing a single solver to run at a different rate.

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),        # global timestep
    rigid_options=gs.options.RigidOptions(dt=0.005),   # rigid solver only, overrides the global dt
    # mpm_options left unset -> the MPM solver, if used, inherits dt=0.01
)
```

The same inheritance applies to `gravity`. Settings that are meaningful only to one solver (for example `RigidOptions.constraint_solver` or `RigidOptions.max_collision_pairs`) live solely on that solver's options and have no global counterpart.

## Scene-level option groups

Each of these is an optional argument to `gs.Scene(...)`. Pass an instance to configure that component; omit it to accept the defaults.

| Options class | `Scene` argument | Configures |
|---|---|---|
| `gs.options.SimOptions` | `sim_options` | Global timestep, gravity, substeps, differentiable mode. |
| `gs.options.BaseCouplerOptions` | `coupler_options` | Coupling between solvers. Concrete variants: `LegacyCouplerOptions`, `SAPCouplerOptions`, `IPCCouplerOptions`. |
| `gs.options.RigidOptions` | `rigid_options` | Rigid-body dynamics: contact, collision, constraints, integrator. |
| `gs.options.MPMOptions` | `mpm_options` | Material Point Method solver (elastic, plastic, granular, fluid). |
| `gs.options.SPHOptions` | `sph_options` | Smoothed Particle Hydrodynamics solver (fluids, granular flow). |
| `gs.options.FEMOptions` | `fem_options` | Finite Element Method solver (elastic material). |
| `gs.options.SFOptions` | `sf_options` | Stable Fluid solver (Eulerian gaseous simulation). |
| `gs.options.PBDOptions` | `pbd_options` | Position-Based Dynamics solver (cloth, deformables, liquids, particles). |
| `gs.options.KinematicOptions` | `kinematic_options` | Kinematic (non-dynamic) entities. |
| `gs.options.ToolOptions` | `tool_options` | Legacy tool solver. Slated for deprecation. |
| `gs.options.VisOptions` | `vis_options` | Visualization independent of any viewer or camera. |
| `gs.options.ViewerOptions` | `viewer_options` | The interactive viewer: camera pose, resolution, refresh rate. |
| `gs.options.ProfilingOptions` | `profiling_options` | Timing and FPS reporting. |
| `gs.renderers.RendererOptions` | `renderer` | Rendering backend: `Rasterizer`, `RayTracer`, or `BatchRenderer`. |

The scene- and solver-level options are documented in the {doc}`simulator, coupler, and solver options reference </api_reference/options/simulator_coupler_and_solver_options/index>`; the viewer, visualization, and renderer options in the {doc}`visualization reference </api_reference/visualization/index>`.

:::{note}
Not every solver runs in every scene. A solver is only active once you add an entity whose material targets it: adding a rigid entity activates the rigid solver, and so on. Options for an inactive solver are simply unused.
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

- **Morph:** the entity's geometry and initial pose. See {doc}`/user_guide/getting_started/hello_genesis` for loading morphs and the {doc}`morph API </api_reference/options/morph/index>`.
- **Material:** how the entity responds to physical forces, and which solver simulates it. See {doc}`/user_guide/physics/beyond_rigid_bodies`.
- **Surface:** how the entity looks when rendered. See {doc}`/user_guide/rendering/surfaces_textures`.

## See also

- {doc}`/user_guide/getting_started/hello_genesis`: the minimal scene that uses these options.
- {doc}`/user_guide/interaction/visualization`: the interactive viewer and command-line tools.
- {doc}`/user_guide/rendering/rendering`: cameras, image types, video, and rendering backends.
- {doc}`Options API reference </api_reference/options/index>`: every option class and its fields.
