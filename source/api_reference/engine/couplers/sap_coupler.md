# `SAPCoupler`

The `SAPCoupler` resolves cross-solver contact with the Semi-Analytic Primal (SAP) contact solver used in [Drake](https://drake.mit.edu/). It targets accurate rigid-deformable contact, including hydroelastic contact against implicit FEM bodies. Select it by passing `gs.options.SAPCouplerOptions` to the scene.

## Options

Configures the inter-solver coupler built on the Semi-Analytic Primal (SAP) contact solver, including its solver iteration counts and convergence tolerances.

```{eval-rst}
.. autoclass:: genesis.options.solvers.SAPCouplerOptions
```

## Configuration

Coupling happens automatically as the scene steps; there is no per-step coupling call. `SAPCouplerOptions` exposes the SAP convergence controls (`n_sap_iterations`, `n_pcg_iterations`, `sap_convergence_atol`), the contact stiffnesses (`hydroelastic_stiffness` and `point_contact_stiffness`, both `1e8` by default), and the per-pair contact types (`fem_floor_contact_type`, `rigid_rigid_type`, and related fields). See the Options section above for the full list. For usage, see {doc}`/user_guide/theory/couplers/index`.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
