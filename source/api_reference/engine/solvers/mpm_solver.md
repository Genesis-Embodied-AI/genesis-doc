# MPMSolver

The `MPMSolver` implements the Material Point Method (MPM) for simulating a wide range of materials including elastic solids, granular materials, fluids, and phase transitions.

## Overview

MPM combines:

- **Lagrangian particles**: Track material points
- **Eulerian grid**: Solve momentum equations
- **Particle-grid transfers**: MLS-MPM for stability

## Supported Materials

| Material | Description |
|----------|-------------|
| `MPM.Elastic` | Neo-Hookean elasticity |
| `MPM.ElastoPlastic` | Plasticity with yield |
| `MPM.Sand` | Drucker-Prager granular |
| `MPM.Snow` | Snow plasticity |
| `MPM.Liquid` | Weakly compressible fluid |
| `MPM.Muscle` | Active muscle material |

## Usage

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

## Configuration

Key options in `MPMOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `dt` | float | Internal timestep |
| `lower_bound` | tuple | Grid lower corner |
| `upper_bound` | tuple | Grid upper corner |
| `grid_density` | int | Grid cells per unit |
| `particle_size` | float | Particle spacing |

## Grid Setup

MPM requires a background grid for computation:

```python
mpm_options = gs.options.MPMOptions(
    lower_bound=(-2, -2, 0),   # Grid min
    upper_bound=(2, 2, 4),     # Grid max
    grid_density=128,          # Resolution
)
```

## Material Parameters

### Elastic Material

```python
material = gs.materials.MPM.Elastic(
    E=1e5,       # Young's modulus (Pa)
    nu=0.3,      # Poisson's ratio
    rho=1000,    # Density (kg/m^3)
)
```

### Granular (Sand)

```python
material = gs.materials.MPM.Sand(
    E=1e6,
    nu=0.2,
    rho=1500,
    friction_angle=30,  # degrees
)
```

## See Also

- {doc}`/api_reference/entity/mpm_entity` - MPMEntity
- {doc}`/api_reference/material/mpm/index` - MPM materials
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/mpm_options` - Full options
