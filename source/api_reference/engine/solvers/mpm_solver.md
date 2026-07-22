# `MPMSolver`

The `MPMSolver` implements the Material Point Method (MPM) for simulating a wide range of materials including elastic solids, granular materials, fluids, and phase transitions. It combines Lagrangian particles that track material points with a background Eulerian grid that solves the momentum equations, transferring between them with MLS-MPM for stability. The materials it supports are listed in {doc}`/api_reference/entity/material/mpm/index`.

## Usage

The solver activates when the scene contains an MPM entity. Configure the background grid through `MPMOptions`; see {doc}`/api_reference/engine/solvers/mpm_options` for the full option set.

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    mpm_options=gs.options.MPMOptions(
        dt=1e-4,
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
        grid_density=64,
    ),
)

# Add MPM entity
soft_box = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.2, 0.2, 0.2)),
    material=gs.materials.MPM.Elastic(
        E=1e5,      # Young's modulus
        nu=0.3,     # Poisson's ratio
        rho=1000,   # Density
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## See also

- {doc}`/api_reference/entity/mpm_entity`: MPMEntity.
- {doc}`/api_reference/entity/material/mpm/index`: MPM materials.
- {doc}`/api_reference/engine/solvers/mpm_options`: full options.
