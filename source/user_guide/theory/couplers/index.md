# Couplers

A single Genesis World scene can run several physics solvers at once: rigid bodies, FEM, MPM, SPH, PBD. A **coupler** is the component that lets those solvers affect each other: it detects contact between entities owned by different solvers and exchanges the forces and state that keep them physically consistent. Without a coupler, each solver would advance in its own world and objects would pass through one another.

You select a coupler by passing a coupler-options object to the {doc}`Scene </api_reference/engine/scene>`. Every variant derives from {py:class}`BaseCouplerOptions <genesis.options.solvers.BaseCouplerOptions>`:

```python
import genesis as gs

scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),  # omit for the default legacy coupler
)
```

Genesis World ships three couplers with different contact models and different trade-offs between speed, accuracy, and the material types they support.

## The three couplers

- **Legacy coupler ({py:class}`LegacyCouplerOptions <genesis.options.solvers.LegacyCouplerOptions>`):** the default, used when you pass no `coupler_options`. It applies impulse-based collision response across every solver pair (rigid, MPM, SPH, PBD, FEM), and each pair can be toggled individually: for example `rigid_mpm=False`. It is the most broadly compatible option and the right starting point for mixed continuum scenes. See {doc}`/user_guide/theory/solvers_and_coupling` for its architecture and parameters.
- **SAP coupler ({py:class}`SAPCouplerOptions <genesis.options.solvers.SAPCouplerOptions>`):** the Semi-Analytic Primal contact solver from [Drake](https://drake.mit.edu/), built for accurate rigid-FEM contact with moderate deformation. It sits between rigid-body dynamics and IPC in cost and fidelity, and suits FEM-style continuum contact where the legacy impulse model is too coarse.
- **IPC coupler ({py:class}`IPCCouplerOptions <genesis.options.solvers.IPCCouplerOptions>`):** Incremental Potential Contact, a smooth barrier-based model for cloth and highly deformable bodies, both elastic and plastic. It handles rich soft-body interaction directly from vertex positions, with rigid bodies represented as affine bodies (ABD), and is the choice when contact must stay intersection-free and stable under large deformation.

## Choosing a coupler

| Coupler | Contact model | Best for | Notable requirements |
|---|---|---|---|
| Legacy (default) | Impulse-based response | Mixed rigid + MPM/SPH/PBD/FEM scenes; general use | None |
| SAP | Semi-analytic primal (Drake) | Accurate rigid-FEM contact, moderate deformation | 64-bit precision; implicit FEM solver |
| IPC | Barrier-based (incremental potential) | Cloth and large-deformation soft bodies; intersection-free contact | `libuipc` library |

Start with the legacy coupler. Move to SAP when rigid-FEM contact accuracy matters, and to IPC when you need robust, intersection-free contact for cloth or heavily deforming soft bodies. The pages below cover the setup and parameters for the two specialized couplers.

```{toctree}
:hidden:
:maxdepth: 1

ipc_coupler
sap_coupler
```
