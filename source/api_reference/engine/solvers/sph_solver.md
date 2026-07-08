# SPHSolver

The `SPHSolver` implements Smoothed Particle Hydrodynamics for liquid simulation.

## Overview

SPH approximates fluid dynamics with particles:

- Pressure forces from local density.
- Viscosity forces from velocity differences.
- Surface tension.
- Free-surface handling.

Two pressure solvers are available through `pressure_solver`: weakly compressible SPH (`"WCSPH"`, the default) and divergence-free SPH (`"DFSPH"`).

## Supported materials

| Material | Description |
|----------|-------------|
| `SPH.Liquid` | General liquid |

## Usage

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

## Configuration

Key options in `SPHOptions`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lower_bound` | tuple | `(-100, -100, 0)` | Lower corner of the simulation domain. |
| `upper_bound` | tuple | `(100, 100, 100)` | Upper corner of the simulation domain. |
| `particle_size` | float | `0.02` | Particle diameter in meters. |
| `pressure_solver` | str | `"WCSPH"` | Pressure solver: `"WCSPH"` or `"DFSPH"`. |
| `dt` | float | inherited | Substep duration in seconds. Inherits from `SimOptions` if not set. |

## Material parameters

`SPH.Liquid` parameters and typical values:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rho` | `1000.0` | Rest density in kg/m³ (water). |
| `stiffness` | `50000.0` | State stiffness in N/m²; controls how pressure rises with compression. |
| `exponent` | `7.0` | State exponent; controls how nonlinearly pressure scales with density. |
| `mu` | `0.005` | Dynamic viscosity. |
| `gamma` | `0.01` | Surface tension. |

## See also

- {doc}`/api_reference/entity/sph_entity` — SPHEntity.
- {doc}`/api_reference/material/sph/index` — SPH materials.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sph_options` — full options.
