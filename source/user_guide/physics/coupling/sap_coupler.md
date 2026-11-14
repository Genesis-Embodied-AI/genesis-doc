# SAP coupler

The Semi-Analytic Primal (SAP) coupler resolves contact between rigid bodies and FEM soft bodies with a convex, semi-analytic solver derived from the model Drake uses ([paper](https://arxiv.org/abs/2110.10107)). Use it when a rigid robot manipulates a moderately deformable volumetric object (grasping, pressing, lifting) and you need contact forces that stay stable and accurate under sustained load.

SAP handles two solvers: `Rigid` and `FEM`. For cloth and highly deformable bodies, use the {doc}`IPC coupler </user_guide/physics/coupling/ipc_coupler>` instead; for multi-solver scenes (MPM, SPH, PBD) or differentiable simulation, use the default coupler described in {doc}`Solvers and coupling </user_guide/physics/coupling/index>`.

## Requirements

SAP coupling imposes two hard requirements:

- **Implicit FEM solver:** any FEM entity must be simulated with {py:class}`FEMOptions <genesis.options.solvers.FEMOptions>`(use_implicit_solver=True). Genesis World checks this at build time and raises if it is unmet.
- **Rigid or FEM only:** SAP couples the rigid and FEM solvers. Other solvers (MPM, SPH, PBD) are not supported.

SAP runs in both precisions. Single precision runs fastest, while `precision="64"` solves the contacts about ten times more accurately for a quarter to two thirds more Newton iterations.

SAP does not support differentiable simulation. Calls into the gradient path raise and direct you to the default coupler.

## Minimal example

The complete script is [`examples/sap_coupling/fem_sphere_and_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/fem_sphere_and_cube.py), which drops an FEM cube onto an FEM sphere. Two choices turn SAP coupling on, and the example also picks 64-bit precision for accuracy:

```python
import genesis as gs

gs.init(backend=gs.gpu, precision="64")  # optional: SAP also runs in 32-bit

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1 / 60, substeps=2),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),  # SAP requires implicit FEM
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

Selecting the coupler is a single line: pass {py:class}`SAPCouplerOptions <genesis.options.solvers.SAPCouplerOptions>`() as `coupler_options`. Everything else is a normal Genesis scene. Add a ground plane for the bodies to rest on, then add FEM entities with an elastic material and step as usual:

```python
scene.add_entity(gs.morphs.Plane())
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.0, 0.0, 0.1), radius=0.1),
    material=gs.materials.FEM.Elastic(model="linear_corotated", E=1e5, nu=0.4),
)
```

## Solver parameters

SAP runs an outer convex solver whose Newton steps are solved by a preconditioned conjugate gradient (PCG) inner loop and refined by a line search. Each solve stops once it converges, so the iteration counts below are caps rather than fixed costs. The defaults suit typical manipulation scenes; lower `sap_convergence_rtol` when resting contacts slip or a grasp drifts.

| Parameter | Default | Meaning |
|---|---|---|
| `n_sap_iterations` | `100` | Maximum Newton iterations per substep |
| `n_pcg_iterations` | `100` | Maximum PCG iterations per Newton step |
| `n_linesearch_iterations` | `100` | Maximum line-search iterations per Newton step |
| `sap_convergence_atol` | `None` | Absolute tolerance on the gradient of the SAP cost, in momentum units; `None` uses the relative tolerance alone |
| `sap_convergence_rtol` | `None` | Tolerance relative to the momentum of the scene; `None` takes `1e-4` in 64-bit and `1e-3` in 32-bit |
| `pcg_threshold` | `1e-2` | Reduction of the squared PCG residual relative to its initial value |
| `linesearch_ftol` | `1e-6` | Sufficient-decrease tolerance for exact line search |
| `linesearch_max_step_size` | `1.5` | Maximum line-search step size |
| `sap_taud` | `0.1` | Contact dissipation time scale |
| `sap_beta` | `0.125` | Stiffness of rigid-body contacts, as the settling time of a resting body in substeps; smaller is stiffer |
| `sap_sigma` | `1e-3` | Friction regularization |
| `enable_lagged_friction` | `True` | Scale friction with the normal force of the previous substep, so sliding bodies stay on the surface |
| `stiction_tolerance` | `1e-4` | Sliding speed in m/s below which lagged friction holds a contact as sticking |

## Contact model parameters

SAP models contact with a compliant, hydroelastic pressure field. The stiffness parameter sets how firmly surfaces resist interpenetration, and the capacity parameters size the contact buffers.

| Parameter | Default | Meaning |
|---|---|---|
| `hydroelastic_stiffness` | `1e8` | Stiffness of the hydroelastic (pressure-field) contact, which also bounds the stiffness of FEM-floor contact |
| `enable_fem_self_collision` | `True` | Let distant parts of one FEM entity collide, such as a long body folding onto itself; distinct FEM entities always collide |
| `enable_fem_neutral_collision` | `False` | Also collide parts of an FEM entity adjacent in its rest shape, for thin bodies whose faces get pressed together |
| `max_collision_pairs` | `32768` | Maximum collision pairs of each kind of contact per environment |
| `max_contacts` | `4096` | Maximum contact points of each kind of contact per environment |

Exceeding `max_collision_pairs` or `max_contacts` at runtime halts the simulation with an error naming the option. Raise it for large or finely meshed contact patches, at a memory cost proportional to it and to the number of environments. `enable_fem_neutral_collision` multiplies the collision pairs of fine meshes, so it usually needs a much larger `max_collision_pairs`.

The floor is the rigid ground plane of the scene, added with `gs.morphs.Plane()`. The surface vertices of FEM entities and the vertices of rigid bodies touch it. SAP supports a single fixed plane facing up as ground, and raises at build on a terrain, a second plane, or a tilted or movable plane. A scene without a ground plane has no floor contact.

## Grasping a deformable object

[`examples/sap_coupling/franka_grasp_fem_sphere.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/franka_grasp_fem_sphere.py) has a Franka arm grasp and lift an FEM sphere, the workload SAP is built for. A rigid-cube variant lives in [`franka_grasp_rigid_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/franka_grasp_rigid_cube.py).

The default tolerances hold a steady grasp. The example only disables self-collision on the arm so the fingers can close fully:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1 / 60, substeps=2),
    rigid_options=gs.options.RigidOptions(enable_self_collision=False),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

To hold a target vertex of an FEM body in place (a fixed constraint rather than a grasp), see [`fem_fixed_constraint.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/fem_fixed_constraint.py), which drives a vertex with `set_vertex_constraints`. `FEMOptions(max_vertex_constraints=...)` caps the constrained vertices per environment at 64 by default, and constraining one more raises.

## When to use SAP

- **Use SAP** for rigid-FEM manipulation of moderately deformable volumetric bodies, where you need stable, accurate contact under sustained load.
- **Use the {doc}`IPC coupler </user_guide/physics/coupling/ipc_coupler>`** for cloth and highly deformable soft bodies.
- **Use the default coupler** ({doc}`Solvers and coupling </user_guide/physics/coupling/index>`) for scenes with MPM, SPH, or PBD, for rigid-only simulation, or when you need gradients for differentiable simulation.

## See also

- {doc}`IPC coupler </user_guide/physics/coupling/ipc_coupler>`: barrier-based contact for cloth and highly deformable bodies.
- {doc}`Solvers and coupling </user_guide/physics/coupling/index>`: how solvers and couplers fit together.
- {doc}`FEM options </api_reference/engine/solvers/fem_solver>` and {doc}`FEM elastic material </api_reference/engine/material/fem/elastic>`: configuring the deformable bodies SAP couples.
