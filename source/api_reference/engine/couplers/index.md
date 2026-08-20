# Couplers

A coupler transfers forces and state between the physics solvers so that different material types interact in a shared scene, for example a rigid gripper grasping a soft object. The simulator holds exactly one coupler, selected by the coupler options you pass to the scene. For guidance on choosing between them, see {doc}`/user_guide/theory/coupling/index`.

## Coupler types

```{toctree}
:titlesonly:

legacy_coupler
sap_coupler
ipc_coupler
```

## Base options

Every coupler options class inherits these fields from `BaseCouplerOptions`.

```{eval-rst}
.. autoclass:: genesis.options.solvers.BaseCouplerOptions
```

## See also

- {doc}`/user_guide/theory/coupling/index`: choosing and configuring a coupler.
- {doc}`/api_reference/engine/solvers/index`: the physics solvers being coupled.
