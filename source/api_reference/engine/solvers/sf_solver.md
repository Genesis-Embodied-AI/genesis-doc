# SFSolver

The `SFSolver` is the Stable Fluid solver: a grid-based (Eulerian) solver for gaseous phenomena such as smoke. It advects a velocity field and one or more scalar density fields on a fixed 3D grid, then makes the velocity field divergence-free with a Jacobi pressure projection.

It simulates the `SF.Smoke` material; see {doc}`/api_reference/engine/material/sf`. For usage and behavior, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.SFOptions
```

## See also

- {doc}`/api_reference/engine/material/sf`: the smoke material simulated by this solver.
