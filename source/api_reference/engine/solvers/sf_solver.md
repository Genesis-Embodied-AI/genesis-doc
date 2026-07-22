# `SFSolver`

The `SFSolver` is the Stable Fluid solver: a grid-based (Eulerian) solver for gaseous phenomena such as smoke. It advects a velocity field and one or more scalar density fields on a fixed 3D grid, then makes the velocity field divergence-free with a Jacobi pressure projection.

Unlike the particle- and mesh-based solvers, the Stable Fluid solver does not track Lagrangian entities. It solves everything on a uniform grid whose resolution you set through `SFOptions.res`, and gas is injected by velocity jets that you register on the solver. It simulates the `SF.Smoke` material; see {doc}`/api_reference/entity/material/sf`.

## Usage

The smoke example drives the solver with a set of velocity jets, then reads the density grid back for rendering. Jets are registered directly on the solver with `set_jets`.

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1e-2),
    sf_options=gs.options.SFOptions(
        res=384,          # grid cells per axis (res x res x res)
        solver_iters=200,  # Jacobi iterations for pressure projection
        decay=0.025,       # per-step density decay
    ),
)

# `jets` is a list of jet objects, each exposing get_tan_dir / get_factor.
# See examples/smoke.py for a complete jet implementation.
scene.sim.sf_solver.set_jets(jets)

scene.build()

for _ in range(200):
    density = scene.sim.sf_solver.grid.q.to_numpy()  # shape (res, res, res, n_jets)
    scene.step()
```

See `examples/smoke.py` for the full runnable example, including the jet class and the code that writes the density field to images.

Configure the grid resolution and projection through `SFOptions`; see {doc}`/api_reference/engine/solvers/sf_options` for the full option set.

## Behavior and guarantees

- The solver is active only once at least one jet is registered with `set_jets`. With no jets, it allocates no fields and does nothing.
- Each substep advects the velocity and scalar fields (RK3 backtracing with trilinear interpolation), injects momentum at the jets, computes divergence, runs `solver_iters` Jacobi pressure iterations, and subtracts the pressure gradient to keep the velocity field divergence-free.
- State lives on a fixed grid; there are no per-entity get/set state methods, and the solver does not currently participate in checkpointing.

## See also

- {doc}`/api_reference/entity/material/sf`: the smoke material simulated by this solver.
- {doc}`/api_reference/engine/solvers/sf_options`: full options.
