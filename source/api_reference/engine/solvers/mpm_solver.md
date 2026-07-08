# MPMSolver

The `MPMSolver` implements the Material Point Method (MPM) for simulating a wide range of materials including elastic solids, granular materials, fluids, and phase transitions.

## Overview

MPM combines:

- **Lagrangian particles:** track material points.
- **Eulerian grid:** solve the momentum equations.
- **Particle-grid transfers:** MLS-MPM for stability.

## Supported materials

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

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dt` | float | inherited | Substep duration in seconds. Inherits from `SimOptions` if not set. |
| `lower_bound` | tuple | `(-1, -1, 0)` | Lower corner of the simulation domain. |
| `upper_bound` | tuple | `(1, 1, 1)` | Upper corner of the simulation domain. |
| `grid_density` | float | `64` | Grid cells per meter. |
| `particle_size` | float | auto | Particle diameter in meters; derived from `grid_density` if not set. |
| `enable_CPIC` | bool | `False` | Enable CPIC for coupling with thin objects. |

## Grid setup

MPM requires a background grid for computation:

```python
mpm_options = gs.options.MPMOptions(
    lower_bound=(-2, -2, 0),   # Grid min
    upper_bound=(2, 2, 4),     # Grid max
    grid_density=128,          # Resolution
)
```

## Material parameters

### Elastic material

```python
material = gs.materials.MPM.Elastic(
    E=1e5,     # Young's modulus, Pa
    nu=0.3,    # Poisson's ratio
    rho=1000,  # density, kg/m^3
)
```

### Granular (sand)

```python
material = gs.materials.MPM.Sand(
    E=1e6,
    nu=0.2,
    rho=1500,
    friction_angle=30,  # degrees
)
```

## See also

- {doc}`/api_reference/entity/mpm_entity` — MPMEntity.
- {doc}`/api_reference/material/mpm/index` — MPM materials.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/mpm_options` — full options.
