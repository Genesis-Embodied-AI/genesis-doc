# `SFSolver`

The `SFSolver` is the Stable Fluid solver: a grid-based (Eulerian) solver for gaseous phenomena such as smoke. It advects a velocity field and one or more scalar density fields on a fixed 3D grid, then makes the velocity field divergence-free with a Jacobi pressure projection.

Unlike the particle- and mesh-based solvers, the Stable Fluid solver does not track Lagrangian entities. It solves everything on a uniform grid whose resolution you set through `SFOptions.res`, and gas is injected by velocity jets that you register on the solver. It simulates the `SF.Smoke` material; see {doc}`/api_reference/entity/material/sf`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.SFOptions
```

## Usage

The solver is driven by velocity jets registered directly on it with `set_jets`, and its density grid is read back for rendering. See `examples/smoke.py` for the full runnable example, including the jet class and the code that writes the density field to images.

Configure the grid resolution and projection through the `SFOptions` documented above.

## Behavior and guarantees

- The solver is active only once at least one jet is registered with `set_jets`. With no jets, it allocates no fields and does nothing.
- Each substep advects the velocity and scalar fields (RK3 backtracing with trilinear interpolation), injects momentum at the jets, computes divergence, runs `solver_iters` Jacobi pressure iterations, and subtracts the pressure gradient to keep the velocity field divergence-free.
- State lives on a fixed grid; there are no per-entity get/set state methods, and the solver does not currently participate in checkpointing.

## See also

- {doc}`/api_reference/entity/material/sf`: the smoke material simulated by this solver.
