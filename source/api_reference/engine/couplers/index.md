# Couplers

A coupler transfers forces and state between the physics solvers so that different material types interact in a shared scene, for example a rigid gripper grasping a soft object. The simulator holds exactly one coupler, selected by the coupler options you pass to the scene.

## Available couplers

| Coupler | What it is | Best for |
|---------|------------|----------|
| **LegacyCoupler** | The default coupler that handles all cross-solver pairs (rigid, MPM, SPH, PBD, FEM), slated for deprecation | General multi-physics scenes |
| **SAPCoupler** | A Semi-Analytic Primal (SAP) contact solver, as used in Drake | Accurate rigid-deformable contact with implicit FEM |
| **IPCCoupler** | Incremental Potential Contact, a barrier-based, intersection-free contact model | Cloth and large-deformation soft bodies |

See {doc}`/user_guide/advanced_topics/couplers/index` for guidance on choosing between them.

## Configuration

The coupler is chosen by the type of `coupler_options` passed to the scene. Omitting it selects the legacy coupler.

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

Once the coupler is set, coupling between entities happens automatically as the scene steps; there is no per-step coupling call.

## Coupler types

```{toctree}
:titlesonly:

legacy_coupler
sap_coupler
ipc_coupler
```

## See also

- {doc}`/user_guide/advanced_topics/couplers/index`: choosing and configuring a coupler
- {doc}`/api_reference/engine/solvers/index`: the physics solvers being coupled
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/coupler_options`: coupler options reference
