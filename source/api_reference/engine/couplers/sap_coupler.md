# `SAPCoupler`

The `SAPCoupler` resolves cross-solver contact with the Semi-Analytic Primal (SAP) contact solver used in [Drake](https://drake.mit.edu/). It targets accurate rigid-deformable contact, including hydroelastic contact against implicit FEM bodies. Select it by passing `gs.options.SAPCouplerOptions` to the scene.

## Minimal example

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

Coupling then happens automatically as the scene steps; there is no per-step coupling call.

## Configuration

`SAPCouplerOptions` exposes the SAP convergence controls (`n_sap_iterations`, `n_pcg_iterations`, `sap_convergence_atol`), the contact stiffnesses (`hydroelastic_stiffness` and `point_contact_stiffness`, both `1e8` by default), and the per-pair contact types (`fem_floor_contact_type`, `rigid_rigid_type`, and related fields). See {doc}`/api_reference/engine/couplers/sap_coupler_options` for the full list.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
- {doc}`/api_reference/engine/couplers/sap_coupler_options`: SAP coupler options.
