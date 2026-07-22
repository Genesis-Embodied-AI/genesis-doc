# `MPMSolver`

The `MPMSolver` implements the Material Point Method (MPM) for simulating a wide range of materials including elastic solids, granular materials, fluids, and phase transitions. It combines Lagrangian particles that track material points with a background Eulerian grid that solves the momentum equations, transferring between them with MLS-MPM for stability. The materials it supports are listed in {doc}`/api_reference/entity/material/mpm/index`.

## Usage

The solver activates when the scene contains an MPM entity. Configure the background grid through `MPMOptions`; see {doc}`/api_reference/engine/solvers/mpm_options` for the full option set. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## See also

- {doc}`/api_reference/entity/mpm_entity`: MPMEntity.
- {doc}`/api_reference/entity/material/mpm/index`: MPM materials.
- {doc}`/api_reference/engine/solvers/mpm_options`: full options.
