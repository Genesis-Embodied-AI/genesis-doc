# Solvers and coupling

A single Genesis World `Scene` can hold a rigid robot, a pool of water, a pile of sand, and a sheet of cloth at once. It does this by running several physics **solvers** side by side and letting a **coupler** exchange forces wherever materials from different solvers meet. This page explains what each solver models, how they share one scene and one set of state fields, and how coupling moves momentum across material boundaries.

It is a conceptual overview. For the equations each solver integrates, see {doc}`Non-rigid dynamics <nonrigid_models>`; to pick a solver and run it, see {doc}`Beyond rigid bodies </user_guide/getting_started/beyond_rigid_bodies>`; for the contact backends, see {doc}`Couplers <couplers/index>`.

## The solvers

A **solver** is the set of algorithms that advances one family of materials. You never instantiate a solver directly. You assign a `material` to an entity, and the scene routes that entity to the solver its material belongs to. `gs.materials.MPM.Liquid` goes to the Material Point Method solver; `gs.materials.Rigid` goes to the rigid solver, and so on.

Genesis World ships six physics solvers, each suited to a different representation of matter:

| Solver | Models | Representation |
|---|---|---|
| **Rigid** | Articulated robots and rigid bodies, joints, contacts | Reduced-coordinate multibody dynamics |
| **MPM** (Material Point Method) | Elastic solids, plastics, sand, snow, liquids | Hybrid: particles carry state, a background grid resolves forces |
| **FEM** (Finite Element Method) | Stiff elastic solids and volumetric muscles | Tetrahedral mesh |
| **PBD** (Position-Based Dynamics) | Cloth, ropes, and topology-preserving deformables | Particles linked by constraints |
| **SPH** (Smoothed-Particle Hydrodynamics) | Free-surface liquids with real fluid parameters | Particles (purely Lagrangian) |
| **SF** (Stable Fluids) | Smoke and gas | Fixed Eulerian grid |

The rigid solver is the default. In {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` the Franka arm had no explicit material, so it defaulted to `gs.materials.Rigid` and ran on the rigid solver. Assign a material from another family and its solver runs alongside.

:::{note}
Two internal solvers round out the set: a **kinematic** solver for scripted, non-dynamic motion and a **tool** solver for driven manipulators. They participate in coupling but are not chosen through the material families above.
:::

## One scene, many solvers

The scene owns a single `simulator`, and the simulator owns one instance of every solver plus one coupler. This shared-state design is what makes cross-material simulation practical:

- **Every entity lives in exactly one solver.** When you call `scene.add_entity`, the simulator inspects the material and hands the entity to the matching solver. That solver stores the entity's state.
- **State lives in flat, global fields.** Each solver keeps its data in Quadrants fields that span all of its entities at once, indexed by offset rather than per-entity objects. An MPM solver holds one particle array for the whole scene; a rigid solver holds one degree-of-freedom (**dof**) array. See {doc}`Concepts <concepts>` for how local and global indexing map onto these fields.
- **Coupling touches solver memory without copies.** Because the fields are laid out for the GPU, the coupler runs compiled kernels that read and write the memory of several solvers in place. No data is marshalled between solvers each step, which is what keeps multi-solver scenes fast enough to be useful.

At build time the simulator marks each solver active only if it holds at least one entity. Inactive solvers cost nothing, so declaring a scene that *could* hold fluids does not slow down a rigid-only run.

## How coupling works

Solvers advance independently within a timestep, and the coupler reconciles them in between. Each substep runs four phases in order:

- **Preprocess:** the coupler prepares cross-solver data, for example surfacing operations needed by the CPIC variant of MPM.
- **Advance (pre-coupling):** every active solver integrates its own material forward by one substep, ignoring the others.
- **Couple:** the coupler detects contact between entities in different solvers and exchanges momentum so they no longer interpenetrate.
- **Postprocess (post-coupling):** each solver finalizes the substep with the coupled state.

The default coupler resolves contact with an **impulse-based** response. For each candidate contact it queries the signed distance to the rigid or solid geometry and blends the response with a smooth influence weight, so contact turns on gradually rather than snapping. It then splits the relative velocity into a normal and a tangential part, applies a restitution rule along the normal and a Coulomb-friction rule along the tangent, and applies the equal-and-opposite momentum change back on the rigid body as an external force. Three per-geometry material parameters govern the response:

- **`coup_softness`:** the thickness of the contact zone. Larger values spread the influence farther from the surface and soften the impulse.
- **`coup_restitution`:** bounce along the normal, from `0` (perfectly inelastic) to `1` (perfectly elastic).
- **`coup_friction`:** the Coulomb friction coefficient limiting tangential slip.

## Choosing a coupler

The coupler is selected by the type of `coupler_options` you pass to the scene. Genesis World ships three, and the scene defaults to the legacy coupler when you pass nothing:

| Coupler | Options class | Best for | Contact model |
|---|---|---|---|
| **Legacy** (default) | `LegacyCouplerOptions` | Particle and grid solvers (MPM, SPH, PBD) and differentiable simulation | Impulse-based |
| **SAP** | `SAPCouplerOptions` | Accurate rigid-FEM contact, such as grasping deformables | Semi-analytic primal |
| **IPC** | `IPCCouplerOptions` | Cloth and highly deformable bodies in contact with rigid tools | Barrier-based (Incremental Potential Contact) |

All three inherit from `BaseCouplerOptions`. Passing an options object both selects the coupler and configures it:

```python
import genesis as gs

# The scene defaults to LegacyCouplerOptions() if you pass nothing.
scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),  # switch to the SAP coupler
)
```

The SAP and IPC couplers carry requirements the legacy coupler does not (SAP needs 64-bit precision and the implicit FEM solver; IPC needs the `libuipc` library). Their trade-offs and full parameter sets live in {doc}`Couplers <couplers/index>`.

## Enabling and disabling interactions

The legacy coupler activates a pair of solvers only when both are present in the scene *and* the corresponding flag is set. Every pair is enabled by default:

```python
scene = gs.Scene(
    coupler_options=gs.options.LegacyCouplerOptions(
        rigid_mpm=False,  # skip rigid-MPM contact even when both solvers are active
    ),
)
```

The available pair flags on `LegacyCouplerOptions` are `rigid_mpm`, `rigid_sph`, `rigid_pbd`, `rigid_fem`, `mpm_sph`, `mpm_pbd`, `fem_mpm`, and `fem_sph`. A pair with no flag is not coupled by the legacy coupler. Disable a pair you do not need to save the cost of its contact kernels.

## See also

- {doc}`Beyond rigid bodies </user_guide/getting_started/beyond_rigid_bodies>`: choose a solver and run a minimal example for each.
- {doc}`Non-rigid dynamics <nonrigid_models>`: the governing equations and integration scheme behind each solver.
- {doc}`Couplers <couplers/index>`: the SAP and IPC contact backends, their requirements, and parameters.
- {doc}`Concepts <concepts>`: how entity state maps onto each solver's global data fields.
- Runnable cross-solver pairings live in [`examples/coupling`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/coupling).
