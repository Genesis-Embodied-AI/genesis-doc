# `SPHSolver`

The `SPHSolver` implements Smoothed Particle Hydrodynamics for liquid simulation. It approximates fluid dynamics with particles, deriving pressure forces from local density, viscosity forces from velocity differences, and surface tension, with free-surface handling. Two pressure solvers are available through `pressure_solver`: weakly compressible SPH (`"WCSPH"`, the default) and divergence-free SPH (`"DFSPH"`). It simulates the `SPH.Liquid` material; see {doc}`/api_reference/entity/material/sph`.

## Usage

The solver activates when the scene contains an SPH entity. Configure it through `SPHOptions`; see {doc}`/api_reference/engine/solvers/sph_options` for the full option set.

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sph_options=gs.options.SPHOptions(
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
        particle_size=0.02,
    ),
)

# Rigid floor
plane = scene.add_entity(gs.morphs.Plane())

# Add a block of fluid
fluid = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.4, 0.4, 0.4)),
    material=gs.materials.SPH.Liquid(
        rho=1000,   # rest density, kg/m^3
        mu=0.005,   # viscosity
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## See also

- {doc}`/api_reference/entity/sph_entity`: SPHEntity.
- {doc}`/api_reference/entity/material/sph`: SPH materials.
- {doc}`/api_reference/engine/solvers/sph_options`: full options.
