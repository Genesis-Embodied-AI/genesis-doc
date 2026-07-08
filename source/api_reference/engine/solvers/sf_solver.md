# SFSolver

The `SFSolver` is the Stable Fluid solver: a grid-based (Eulerian) solver for gaseous phenomena such as smoke. It advects a velocity field and one or more scalar density fields on a fixed 3D grid, then makes the velocity field divergence-free with a Jacobi pressure projection.

Unlike the particle- and mesh-based solvers, the Stable Fluid solver does not track Lagrangian entities. It solves everything on a uniform grid whose resolution you set through `SFOptions.res`, and gas is injected by velocity jets that you register on the solver.

## Supported materials

| Material | Description |
|----------|-------------|
| `SF.Smoke` | Smoke advected on the stable-fluid grid |

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

## Configuration

Key options in `SFOptions`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `res` | int | 128 | Grid resolution per axis; the grid is `res x res x res`. |
| `solver_iters` | int | 500 | Jacobi iterations for the pressure projection. |
| `decay` | float | 0.99 | Per-step decay applied to the advected scalar (density) field. |
| `inlet_s` | float | 400.0 | Impulse scale applied at the jets when injecting momentum. |
| `dt` | float | inherited | Substep duration in seconds. Inherits from `SimOptions` if not set. |

## Behavior and guarantees

- The solver is active only once at least one jet is registered with `set_jets`. With no jets, it allocates no fields and does nothing.
- Each substep advects the velocity and scalar fields (RK3 backtracing with trilinear interpolation), injects momentum at the jets, computes divergence, runs `solver_iters` Jacobi pressure iterations, and subtracts the pressure gradient to keep the velocity field divergence-free.
- State lives on a fixed grid; there are no per-entity get/set state methods, and the solver does not currently participate in checkpointing.

## See also

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sf_options` — full options.
