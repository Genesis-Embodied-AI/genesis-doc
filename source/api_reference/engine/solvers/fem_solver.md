# `FEMSolver`

The `FEMSolver` implements the Finite Element Method for simulating deformable solids on tetrahedral meshes. It supports several constitutive models (linear, stable Neo-Hookean, linear corotated), handles large deformations, and offers an explicit integrator by default with an optional implicit solver for stability at larger time steps. The materials it supports are listed in {doc}`/api_reference/entity/material/fem/index`.

## Usage

The solver activates when the scene contains an FEM entity. Configure it through `FEMOptions`; see {doc}`/api_reference/engine/solvers/fem_options` for the full option set. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Vertex constraints

Pin vertices to fixed targets or to a rigid link with `set_vertex_constraints`. Under the implicit solver, set `enable_vertex_constraints=True` first. See {doc}`/user_guide/physics/soft_robots` for muscle-driven deformable bodies.

## See also

- {doc}`/api_reference/entity/fem_entity`: FEMEntity.
- {doc}`/api_reference/entity/material/fem/index`: FEM materials.
- {doc}`/api_reference/engine/solvers/fem_options`: full options.
