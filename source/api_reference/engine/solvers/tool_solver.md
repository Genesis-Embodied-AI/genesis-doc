# ToolSolver

The `ToolSolver` handles kinematic tools and end-effectors that drive other physics objects through one-way coupling into the soft solvers (MPM, FEM, PBD, SPH). A `ToolEntity` has no internal dynamics and is built from a single mesh. It is a temporary workaround for differentiable rigid-soft interaction and will be removed once the `RigidSolver` supports differentiability directly.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.ToolOptions
```

## See also

- {doc}`/api_reference/engine/material/tool`: the tool material and its parameters.
- {doc}`/api_reference/engine/couplers/index`: coupling with other solvers.
