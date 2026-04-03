# Physics Engine

Genesis integrates multiple physics solvers into a unified framework, enabling simulation of diverse physical phenomena including rigid bodies, soft bodies, fluids, and their interactions.

## Architecture Overview

```
Scene
└── Simulator
    ├── Solvers (physics computation)
    │   ├── RigidSolver - Rigid body dynamics
    │   ├── MPMSolver - Material Point Method
    │   ├── FEMSolver - Finite Element Method
    │   ├── PBDSolver - Position Based Dynamics
    │   ├── SPHSolver - Smoothed Particle Hydrodynamics
    │   ├── SFSolver - String/Fiber dynamics
    │   └── ToolSolver - Kinematic constraints
    │
    └── Couplers (physics interactions)
        ├── LegacyCoupler - Impulse-based coupling
        ├── SAPCoupler - Spatial acceleration
        └── IPCCoupler - Incremental Potential Contact
```

## Simulation Loop

A typical simulation step involves:

1. **Pre-step**: Prepare solver states
2. **Solver steps**: Each solver advances its physics
3. **Coupling**: Handle interactions between different physics types
4. **Post-step**: Update render state, sensors

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,          # Timestep
        substeps=4,       # Physics substeps per step
        gravity=(0, 0, -9.81),
    ),
)

# Add entities...
scene.build()

# Each step() executes the full simulation loop
for i in range(1000):
    scene.step()
```

## Selecting Solvers

Solvers are automatically selected based on entity types and materials:

| Entity/Material | Solver |
|-----------------|--------|
| `RigidEntity`, URDF, MJCF | RigidSolver |
| `MPMEntity`, MPM materials | MPMSolver |
| `FEMEntity`, FEM materials | FEMSolver |
| `PBDEntity`, cloth/soft materials | PBDSolver |
| `SPHEntity`, SPH liquid | SPHSolver |
| String/fiber materials | SFSolver |

## Solver Configuration

Each solver has dedicated options:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        substeps=4,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_collision=True,
        enable_joint_limit=True,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
    ),
)
```

## Components

```{toctree}
:titlesonly:

solvers/index
couplers/index
states/index
```

## See Also

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/index` - Solver configuration
- {doc}`/api_reference/entity/index` - Entity types for each solver
