# SAPCoupler

The `SAPCoupler` resolves cross-solver contact with the Semi-Analytic Primal (SAP) contact solver used in [Drake](https://drake.mit.edu/). It targets accurate rigid-deformable contact, including hydroelastic contact against implicit FEM bodies. Select it by passing `gs.options.SAPCouplerOptions` to the scene.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.SAPCouplerOptions
```

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
