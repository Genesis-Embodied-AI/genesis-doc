# FEMSolver

The `FEMSolver` implements the Finite Element Method for simulating deformable solids with high accuracy.

## Overview

The FEM solver:

- Uses tetrahedral mesh elements
- Supports various constitutive models
- Handles large deformations (geometric nonlinearity)
- GPU-accelerated assembly and solve

## Supported Materials

| Material | Description |
|----------|-------------|
| `FEM.Elastic` | Linear/nonlinear elasticity |
| `FEM.Muscle` | Active muscle contraction |

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    fem_options=gs.options.FEMOptions(
        dt=1e-3,
        damping=0.1,
    ),
)

# Add FEM entity
soft_body = scene.add_entity(
    gs.morphs.Mesh(file="soft_object.obj"),
    material=gs.materials.FEM.Elastic(
        E=1e5,
        nu=0.4,
        rho=1000,
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `FEMOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `dt` | float | Internal timestep |
| `damping` | float | Rayleigh damping coefficient |
| `iterations` | int | Solver iterations |

## Boundary Conditions

Apply fixed boundary conditions:

```python
# Fix bottom vertices
soft_body.fix_vertices(z_min=0.01)

# Apply external forces
soft_body.apply_force(vertex_ids, force_vector)
```

## See Also

- {doc}`/api_reference/entity/fem_entity` - FEMEntity
- {doc}`/api_reference/material/fem/index` - FEM materials
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/fem_options` - Full options
