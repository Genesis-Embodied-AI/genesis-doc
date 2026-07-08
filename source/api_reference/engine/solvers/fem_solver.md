# FEMSolver

The `FEMSolver` implements the Finite Element Method for simulating deformable solids on tetrahedral meshes.

## Overview

The FEM solver:

- Uses tetrahedral mesh elements.
- Supports several constitutive models (linear, stable Neo-Hookean, linear corotated).
- Handles large deformations (geometric nonlinearity).
- Offers an explicit integrator by default and an optional implicit solver.

## Supported materials

| Material | Description |
|----------|-------------|
| `FEM.Elastic` | Elastic solid with selectable constitutive model |
| `FEM.Muscle` | Active muscle contraction |
| `FEM.Cloth` | Thin-shell cloth |

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

# Add an FEM entity
soft_body = scene.add_entity(
    gs.morphs.Mesh(file="soft_object.obj"),
    material=gs.materials.FEM.Elastic(
        E=1e5,     # Young's modulus, Pa
        nu=0.4,    # Poisson's ratio
        rho=1000,  # density, kg/m^3
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `FEMOptions`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dt` | float | inherited | Substep duration in seconds. Inherits from `SimOptions` if not set. |
| `damping` | float | `0.0` | Damping factor. |
| `use_implicit_solver` | bool | `False` | Use the implicit solver, which is more stable at large time steps. |
| `enable_vertex_constraints` | bool | `False` | Allow vertex constraints under the implicit solver. |

## Vertex constraints

Pin vertices to fixed targets or to a rigid link with `set_vertex_constraints`. Under the implicit solver, set `enable_vertex_constraints=True` first.

```python
# Pin the given vertices at their current positions
soft_body.set_vertex_constraints(verts_idx_local=[0, 1, 2])

# Pull vertices toward a target with a soft spring constraint
soft_body.set_vertex_constraints(
    verts_idx_local=[0, 1, 2],
    target_poss=[(0.0, 0.0, 0.5)] * 3,
    is_soft_constraint=True,
    stiffness=1e3,
)
```

## See also

- {doc}`/api_reference/entity/fem_entity` — FEMEntity.
- {doc}`/api_reference/material/fem/index` — FEM materials.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/fem_options` — full options.
