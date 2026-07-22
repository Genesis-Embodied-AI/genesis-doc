# Options

Almost every component in Genesis World is configured through an **Options** class you pass in, and built into a working object when the scene builds (`RigidOptions` -> `RigidSolver`, `IMU` -> `IMUSensor`, and so on). Since the options and the object are two halves of one component, in this API Reference we document each **Options** with the object it configures.


```{eval-rst}
.. autoclass:: genesis.options.options.Options
```

## Options classes

| Reference page | Options |
|---|---|
| {doc}`/api_reference/engine/scene` | `gs.options.ProfilingOptions` |
| {doc}`/api_reference/engine/simulator` | `gs.options.SimOptions` |
| {doc}`/api_reference/engine/solvers/index` | `gs.options.RigidOptions`, `gs.options.MPMOptions`, `gs.options.FEMOptions`, `gs.options.PBDOptions`, `gs.options.SPHOptions`, `gs.options.SFOptions`, `gs.options.ToolOptions`, `gs.options.KinematicOptions` |
| {doc}`/api_reference/engine/couplers/index` | `gs.options.LegacyCouplerOptions`, `gs.options.SAPCouplerOptions`, `gs.options.IPCCouplerOptions` |
| {doc}`/api_reference/engine/entity/morph/index` | `gs.morphs.*` |
| {doc}`/api_reference/engine/entity/surface/index` | `gs.surfaces.*`, `gs.textures.*` |
| {doc}`/api_reference/visualization/viewer` | `gs.options.ViewerOptions`, `gs.options.VisOptions` |
| {doc}`/api_reference/visualization/renderers/index` | `gs.renderers.*` |
| {doc}`/api_reference/engine/sensors/index` | `gs.sensors.*` |
| {doc}`/api_reference/recording/index` | `gs.recorders.*` |

## See also

- {doc}`/api_reference/index`: how the reference is organized, and the options/built-object convention.
- {doc}`/user_guide/configuration/config_system`: configuring a scene through options.
