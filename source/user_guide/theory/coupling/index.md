# Coupling

Solvers advance independently, so on their own a rigid gripper and an FEM block would pass through one another. A **coupler** detects contact between entities owned by different solvers and exchanges the forces and state that keep them consistent. One coupler serves the whole scene, selected by the type of `coupler_options` passed to it:

```python
import genesis as gs

scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),  # omit for the default legacy coupler
)
```

## How coupling works

Each substep runs four phases in order:

- **Preprocess:** the coupler prepares the cross-solver data a solver needs before it integrates, such as the per-particle rigid-surface normals that the compatible particle-in-cell (CPIC) variant of MPM uses to tell which side of a thin geometry each particle is on.
- **Advance (pre-coupling):** every active solver integrates its own material forward by one substep, ignoring the others.
- **Couple:** the coupler detects contact between entities in different solvers and exchanges momentum so they no longer interpenetrate.
- **Postprocess (post-coupling):** each solver finalizes the substep with the coupled state.

The default coupler resolves contact with an **impulse-based** response. For each candidate contact it queries the signed distance to the rigid or solid geometry and blends the response with a smooth influence weight, so contact turns on gradually rather than snapping. It then splits the relative velocity into a normal and a tangential part, applies a restitution rule along the normal and a Coulomb-friction rule along the tangent, and applies the equal-and-opposite momentum change back on the rigid body as an external force. Three per-geometry material parameters govern the response:

- **`coup_softness`:** the thickness of the contact zone. Larger values spread the influence farther from the surface and soften the impulse.
- **`coup_restitution`:** bounce along the normal, from `0` (perfectly inelastic) to `1` (perfectly elastic).
- **`coup_friction`:** the Coulomb friction coefficient limiting tangential slip.

## Choosing a coupler

We ship three couplers, all configured through options classes deriving from {py:class}`BaseCouplerOptions <genesis.options.solvers.BaseCouplerOptions>`, and we default to the legacy coupler because it covers every solver pair.

| Coupler | Contact model | Best for | Requirements |
|---|---|---|---|
| **Legacy** (default) | Impulse-based | Rigid with MPM, SPH, PBD, or FEM; differentiable simulation | None |
| **{doc}`SAP <sap_coupler>`** | Semi-analytic primal, from [Drake](https://drake.mit.edu/) | Rigid-FEM contact under moderate deformation, such as grasping a deformable | 64-bit precision; implicit FEM solver |
| **{doc}`IPC <ipc_coupler>`** | Barrier-based (Incremental Potential Contact) | Cloth and large-deformation soft bodies; intersection-free contact | `libuipc` library |

SAP raises rigid-FEM contact accuracy where the impulse model is too coarse, and IPC keeps contact intersection-free under large deformation, representing rigid bodies through affine body dynamics (ABD). Both specialized couplers have their own pages for setup and parameters.

## Enabling and disabling interactions

The legacy coupler activates a pair of solvers only when both are present in the scene *and* the corresponding flag is set. Every pair is enabled by default:

```python
scene = gs.Scene(
    coupler_options=gs.options.LegacyCouplerOptions(
        rigid_mpm=False,  # skip rigid-MPM contact even when both solvers are active
    ),
)
```

The available pair flags on `LegacyCouplerOptions` are `rigid_mpm`, `rigid_sph`, `rigid_pbd`, `rigid_fem`, `mpm_sph`, `mpm_pbd`, `fem_mpm`, and `fem_sph`; the legacy coupler couples exactly these pairs. Turning off a pair you do not need saves the cost of running its contact kernels every substep.

## See also

- {doc}`Beyond rigid bodies </user_guide/physics/beyond_rigid_bodies>`: choose a solver and run a minimal example for each.
- {doc}`soft_solvers </user_guide/theory/soft_solvers>`: the solvers being coupled and the models they integrate.
- {doc}`Concepts </user_guide/configuration/concepts>`: how entity state maps onto each solver's global data fields.
- Runnable cross-solver pairings live in [`examples/coupling`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/coupling).

```{toctree}
:hidden:
:maxdepth: 1

ipc_coupler
sap_coupler
```
