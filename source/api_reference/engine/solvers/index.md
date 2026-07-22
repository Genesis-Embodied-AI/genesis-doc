# Solvers

A solver is the physics engine for one class of material. Each solver owns the entities built from its materials, advances their state every substep, and exposes the state back to the scene. A scene can run several solvers at once, so a single simulation can mix rigid robots, deformable solids, cloth, fluids, and smoke. For how solvers exchange forces at their interfaces, see {doc}`/user_guide/theory/solvers_and_coupling`.

You rarely construct a solver directly. You add an entity with a material, and the scene routes it to the matching solver; you configure each solver through its options object.

## Available solvers

| Solver | Method | Simulates |
|---|---|---|
| `RigidSolver` | Rigid body and articulated dynamics | Robots, articulated mechanisms, rigid objects |
| `MPMSolver` | Material Point Method | Elastic and elasto-plastic solids, sand, snow, muscle, liquid |
| `FEMSolver` | Finite Element Method | Elastic solids, muscle, cloth |
| `PBDSolver` | Position Based Dynamics | Cloth, soft (elastic) bodies, liquid, free particles |
| `SPHSolver` | Smoothed Particle Hydrodynamics | Liquids |
| `SFSolver` | Stable Fluid (Eulerian grid) | Gaseous phenomena such as smoke |
| `ToolSolver` | Kinematic tool coupling | Rigid tools that drive soft bodies through one-way differentiable coupling |

Each solver has its own page linked below, and its own options:

- **RigidSolver:** {doc}`rigid_solver`, configured by {doc}`/api_reference/engine/solvers/rigid_options`.
- **MPMSolver:** {doc}`mpm_solver`, configured by {doc}`/api_reference/engine/solvers/mpm_options`.
- **FEMSolver:** {doc}`fem_solver`, configured by {doc}`/api_reference/engine/solvers/fem_options`.
- **PBDSolver:** {doc}`pbd_solver`, configured by {doc}`/api_reference/engine/solvers/pbd_options`.
- **SPHSolver:** {doc}`sph_solver`, configured by {doc}`/api_reference/engine/solvers/sph_options`.
- **SFSolver:** {doc}`sf_solver`, configured by {doc}`/api_reference/engine/solvers/sf_options`.
- **ToolSolver:** {doc}`tool_solver`, configured by {doc}`/api_reference/engine/solvers/tool_options`.

:::{note}
`ToolSolver` is a temporary solver that provides one-way differentiable coupling from a rigid tool to soft bodies. It will be removed once the `RigidSolver` supports differentiability directly.
:::

```{toctree}
:titlesonly:

rigid_solver
rigid_options
mpm_solver
mpm_options
fem_solver
fem_options
pbd_solver
pbd_options
sph_solver
sph_options
sf_solver
sf_options
tool_solver
tool_options
kinematic_options
```

## Shared lifecycle

Every solver derives from a common `Solver` base class and follows the same three-phase lifecycle, driven by the scene rather than called directly:

- **Build:** allocate solver state after `scene.build()`, once the set of entities is known.
- **Step:** advance all owned entities by one substep on each `scene.step()`.
- **Reset:** restore state to the initial conditions, optionally for a subset of environments.

`RigidSolver` additionally derives from an intermediate `KinematicSolver`, which supplies the shared forward-kinematics, rendering, and state get/set pipeline for articulated entities.

## Combining solvers

Adding entities with different materials activates their solvers automatically. All active solvers step together within one `scene.step()`, and forces are exchanged between them by a coupler; see {doc}`/api_reference/engine/couplers/index`. For a worked multi-solver example, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Performance

Solvers run on the GPU through Quadrants, the just-in-time compiler that generates the parallel kernels. Computation is parallelized across particles, grid cells, or elements, and across environments when the scene is built with multiple environments (`n_envs > 1`).

## See also

- {doc}`/user_guide/theory/solvers_and_coupling`: how solvers are combined and coupled.
- {doc}`/api_reference/engine/couplers/index`: the couplers that exchange forces between solvers.
