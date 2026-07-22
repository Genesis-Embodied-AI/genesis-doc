# `PBDSolver`

The `PBDSolver` implements Position Based Dynamics for simulating cloth, soft bodies, and particle systems with fast, stable steps. The materials it supports are listed in {doc}`/api_reference/entity/material/pbd/index`.

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

## Usage

The solver activates when the scene contains a PBD entity. Configure it through `PBDOptions`; see {doc}`/api_reference/engine/solvers/pbd_options` for the full option set.

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

## Constraint types

PBD applies several constraint groups, each with its own iteration count:

- **Stretch constraints:** maintain edge lengths.
- **Bending constraints:** resist folding.
- **Volume constraints:** preserve enclosed volume.
- **Density constraints:** enforce incompressibility for fluids.

Each group has its own iteration count in `PBDOptions`.

## See also

- {doc}`/api_reference/entity/pbd_entity/index`: PBD entities.
- {doc}`/api_reference/entity/material/pbd/index`: PBD materials.
- {doc}`/api_reference/engine/solvers/pbd_options`: full options.
