# PBDSolver

The `PBDSolver` implements Position Based Dynamics for simulating cloth, soft bodies, and particle systems with fast, stable performance.

## Overview

PBD works by:

- Predicting particle positions
- Projecting constraint violations
- Iteratively correcting positions
- Computing velocities from position change

Advantages:
- **Stability**: Unconditionally stable
- **Speed**: Fast iterative solving
- **Controllability**: Direct position control

## Supported Materials

| Material | Description |
|----------|-------------|
| `PBD.Cloth` | Cloth/fabric simulation |
| `PBD.Elastic` | Soft elastic bodies |
| `PBD.Particle` | Particle systems |
| `PBD.Liquid` | Position-based fluids |

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    pbd_options=gs.options.PBDOptions(
        iterations=10,
        damping=0.99,
    ),
)

# Add cloth
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_stiffness=0.9,
        bend_stiffness=0.1,
    ),
)

# Fix top edge
cloth.fix_vertices(y_max=0.99)

scene.build()

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `PBDOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `iterations` | int | Constraint iterations |
| `damping` | float | Velocity damping |
| `gravity` | tuple | Override gravity |

## Constraint Types

PBD uses various constraints:

- **Distance constraints**: Maintain edge lengths
- **Bending constraints**: Resist folding
- **Volume constraints**: Preserve volume
- **Collision constraints**: Handle contacts

## Cloth Example

```python
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(
        stretch_stiffness=0.95,   # Resist stretching
        bend_stiffness=0.05,      # Allow bending
        thickness=0.01,           # Collision thickness
    ),
)
```

## See Also

- {doc}`/api_reference/entity/pbd_entity/index` - PBD entities
- {doc}`/api_reference/material/pbd/index` - PBD materials
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/pbd_options` - Full options
