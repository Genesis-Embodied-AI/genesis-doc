# PBDSolver

The `PBDSolver` implements Position Based Dynamics for simulating cloth, soft bodies, and particle systems with fast, stable steps.

## Overview

PBD works by:

- Predicting particle positions.
- Projecting constraint violations.
- Iteratively correcting positions.
- Recovering velocities from the position change.

Advantages:

- **Stability:** robust at large time steps.
- **Speed:** cheap iterative projection.
- **Controllability:** direct position control.

## Supported materials

| Material | Description |
|----------|-------------|
| `PBD.Cloth` | Cloth and fabric |
| `PBD.Elastic` | Soft elastic (3D) bodies |
| `PBD.Particle` | Free particle systems |
| `PBD.Liquid` | Position-based fluids |

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    pbd_options=gs.options.PBDOptions(
        max_stretch_solver_iterations=4,
        max_bending_solver_iterations=1,
    ),
)

# Add cloth
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_compliance=1e-7,   # m/N; smaller resists stretching more
        bending_compliance=1e-5,   # rad/N; smaller resists bending more
    ),
)

scene.build()

# Pin cloth particles by their local indices
cloth.fix_particles(particles_idx_local=[0, 1, 2])

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `PBDOptions`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_stretch_solver_iterations` | int | `4` | Iterations for the stretch constraints. |
| `max_bending_solver_iterations` | int | `1` | Iterations for the bending constraints. |
| `max_volume_solver_iterations` | int | `1` | Iterations for the volume constraints. |
| `max_density_solver_iterations` | int | `1` | Iterations for the density (fluid) constraints. |
| `particle_size` | float | `1e-2` | Particle diameter in meters, used for self-collision. |
| `gravity` | tuple | inherited | Override gravity. Inherits from `SimOptions` if not set. |

## Constraint types

PBD applies several constraint groups, each with its own iteration count:

- **Stretch constraints:** maintain edge lengths.
- **Bending constraints:** resist folding.
- **Volume constraints:** preserve enclosed volume.
- **Density constraints:** enforce incompressibility for fluids.

## Cloth material parameters

`PBD.Cloth` is parameterized by compliances and relaxation factors rather than raw stiffnesses:

```python
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_compliance=1e-7,   # m/N
        bending_compliance=1e-5,   # rad/N
        stretch_relaxation=0.3,    # smaller weakens the stretch constraint
        bending_relaxation=0.1,    # smaller weakens the bending constraint
        air_resistance=1e-3,       # damping from air drag
    ),
)
```

## See also

- {doc}`/api_reference/entity/pbd_entity/index` — PBD entities.
- {doc}`/api_reference/material/pbd/index` — PBD materials.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/pbd_options` — full options.
