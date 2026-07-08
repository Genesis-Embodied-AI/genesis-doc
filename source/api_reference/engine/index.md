# Physics engine

The engine is the layer beneath {doc}`Scene </api_reference/scene/scene>` that actually advances the simulation. A `Simulator` owns a set of physics **solvers**, a **coupler** that resolves interactions between them, and the per-solver **states** that hold runtime data. You rarely construct these objects directly. The scene builds them from the entities you add and the options you pass, then drives them each time you call `scene.step()`.

This page describes how those pieces fit together and links to the reference for each. For the tunable parameters, see {doc}`/api_reference/options/simulator_coupler_and_solver_options/index`.

## Architecture

A scene holds one simulator. The simulator holds the solvers active in the scene and a single coupler:

```
Scene
└── Simulator
    ├── solvers   — one per active physics method (rigid, MPM, FEM, …)
    └── coupler   — resolves interactions across solvers
```

Each solver runs a specific physics method and is activated only when the scene contains at least one entity that needs it. A solver is chosen by an entity's material:

- **RigidSolver:** rigid-body and articulated dynamics for URDF, MJCF, and rigid morphs.
- **MPMSolver:** Material Point Method for deformable, granular, and viscous materials.
- **FEMSolver:** Finite Element Method for elastic and plastic deformable solids.
- **PBDSolver:** Position Based Dynamics for cloth, soft bodies, and particles.
- **SPHSolver:** Smoothed Particle Hydrodynamics for liquids.
- **SFSolver:** Stable Fluid solver for Eulerian, grid-based gaseous simulation such as smoke.
- **ToolSolver:** kinematic tool bodies that drive one-way, differentiable coupling into soft solvers.

The coupler resolves contact and exchange between entities owned by different solvers, so a rigid gripper can grasp an MPM object or a tool can stir an SPH fluid. One coupler is active per scene:

| Coupler | Method |
|---|---|
| **LegacyCoupler** | General cross-solver coupling; slated for deprecation. |
| **SAPCoupler** | Semi-Analytic Primal (SAP) contact solver, as used in Drake. |
| **IPCCoupler** | Incremental Potential Contact for robust, penetration-free contact. |

## The step loop

`scene.step()` advances the simulation by one control step, which is divided into `substeps` physics substeps. Within each substep the simulator runs the active solvers, invokes the coupler to resolve their interactions, then lets the solvers finish the substep:

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,               # control timestep, seconds
        substeps=4,            # physics substeps per step
        gravity=(0, 0, -9.81), # Z-up, m/s²
    ),
)

# ... add entities ...
scene.build()

for _ in range(1000):
    scene.step()  # runs substeps, coupling, and state updates
```

Each solver reads its parameters from the matching options object, so you can tune solvers independently within one scene:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, substeps=4),
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

## Subsections

```{toctree}
:titlesonly:

solvers/index
couplers/index
states/index
```

- **{doc}`solvers/index`:** the per-method solvers and their interfaces.
- **{doc}`couplers/index`:** cross-solver contact and coupling.
- **{doc}`states/index`:** the runtime state each solver holds, and how to read, save, and restore it.

## See also

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/index`: simulator, solver, and coupler options.
- {doc}`/api_reference/entity/index`: the entity types that select each solver.
