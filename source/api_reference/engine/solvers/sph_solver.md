# SPHSolver

The `SPHSolver` implements Smoothed Particle Hydrodynamics for fluid simulation.

## Overview

SPH approximates fluid dynamics using particles:

- Pressure forces from density
- Viscosity forces from velocity differences
- Surface tension (optional)
- Free surface handling

## Supported Materials

| Material | Description |
|----------|-------------|
| `SPH.Liquid` | General liquid simulation |

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

# Add fluid
fluid = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.4, 0.4, 0.4)),
    material=gs.materials.SPH.Liquid(
        rho=1000,     # Density
        viscosity=0.01,
    ),
)

# Add rigid container
container = scene.add_entity(gs.morphs.Box(
    pos=(0, 0, 0.5),
    size=(0.5, 0.5, 0.5),
    is_rigid=True,
    vis_mode="collision",
))

scene.build()

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `SPHOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `lower_bound` | tuple | Domain lower corner |
| `upper_bound` | tuple | Domain upper corner |
| `particle_size` | float | Particle spacing |
| `dt` | float | Internal timestep |

## Parameters

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| `rho` | Rest density | 1000 kg/m^3 (water) |
| `viscosity` | Dynamic viscosity | 0.001-0.1 |
| `stiffness` | Pressure stiffness | 1000-10000 |

## See Also

- {doc}`/api_reference/entity/sph_entity` - SPHEntity
- {doc}`/api_reference/material/sph/index` - SPH materials
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sph_options` - Full options
