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

The solver activates when the scene contains a PBD entity. Configure it through `PBDOptions`; see {doc}`/api_reference/engine/solvers/pbd_options` for the full option set. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

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
