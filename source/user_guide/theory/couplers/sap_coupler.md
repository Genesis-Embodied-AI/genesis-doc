# SAP coupler

The Semi-Analytic Primal (SAP) coupler resolves contact between rigid bodies and FEM soft bodies with a convex, semi-analytic solver derived from the model Drake uses ([paper](https://arxiv.org/abs/2110.10107)). Reach for it when a rigid robot manipulates a moderately deformable volumetric object (grasping, pressing, lifting) and you need contact forces that stay stable and accurate under sustained load.

SAP handles two solvers: `Rigid` and `FEM`. For cloth and highly deformable bodies, use the {doc}`IPC coupler <ipc_coupler>` instead; for multi-solver scenes (MPM, SPH, PBD) or differentiable simulation, use the default coupler described in {doc}`Solvers and coupling </user_guide/theory/solvers_and_coupling>`.

## Requirements

SAP coupling imposes three hard requirements. Each is checked at build time and raises if unmet:

- **64-bit precision:** initialize with `precision="64"`. The solver is ill-conditioned in 32-bit and refuses to run.
- **Implicit FEM solver:** any FEM entity must be simulated with {py:class}`FEMOptions <genesis.options.solvers.FEMOptions>`(use_implicit_solver=True).
- **Rigid or FEM only:** SAP couples the rigid and FEM solvers. Other solvers (MPM, SPH, PBD) are not supported.

SAP does not support differentiable simulation. Calls into the gradient path raise and direct you to the default coupler.

## Minimal example

The complete script is [`examples/sap_coupling/fem_sphere_and_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/fem_sphere_and_cube.py), which drops an FEM cube onto an FEM sphere. The setup that turns on SAP coupling is these three choices:

```python
import genesis as gs

gs.init(backend=gs.gpu, precision="64")  # SAP requires 64-bit

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1 / 60, substeps=2),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),  # SAP requires implicit FEM
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

Selecting the coupler is a single line: pass {py:class}`SAPCouplerOptions <genesis.options.solvers.SAPCouplerOptions>`() as `coupler_options`. Everything else is a normal Genesis scene. Add FEM entities with an elastic material and step as usual:

```python
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.0, 0.0, 0.1), radius=0.1),
    material=gs.materials.FEM.Elastic(model="linear_corotated", E=1e5, nu=0.4),
)
```

## Solver parameters

SAP runs an outer convex solver whose Newton steps are solved by a preconditioned conjugate gradient (PCG) inner loop and refined by a line search. The defaults below are tuned for typical manipulation scenes; tighten the tolerances when contact forces look noisy or a grasp drifts.

| Parameter | Default | Meaning |
|---|---|---|
| `n_sap_iterations` | `5` | Outer SAP (Newton) iterations per step |
| `n_pcg_iterations` | `100` | Maximum PCG iterations per Newton step |
| `n_linesearch_iterations` | `10` | Maximum line-search iterations per Newton step |
| `sap_convergence_atol` | `1e-6` | Absolute tolerance for SAP convergence |
| `sap_convergence_rtol` | `1e-5` | Relative tolerance for SAP convergence |
| `pcg_threshold` | `1e-6` | Convergence threshold for the PCG inner solve |
| `linesearch_ftol` | `1e-6` | Sufficient-decrease tolerance for exact line search |
| `linesearch_max_step_size` | `1.5` | Maximum line-search step size |
| `sap_taud` | `0.1` | Contact dissipation time scale |
| `sap_beta` | `1.0` | Normal-force regularization |
| `sap_sigma` | `1e-3` | Friction regularization |

## Contact model parameters

SAP models contact with a compliant, hydroelastic pressure field. The stiffness parameters set how firmly surfaces resist interpenetration; the contact-type parameters choose how each contact pair is discretized.

| Parameter | Default | Meaning |
|---|---|---|
| `hydroelastic_stiffness` | `1e8` | Stiffness of the hydroelastic (pressure-field) contact |
| `point_contact_stiffness` | `1e8` | Stiffness of point contact |
| `enable_rigid_fem_contact` | `True` | Couple the rigid and FEM solvers |
| `enable_fem_self_tet_contact` | `True` | Detect FEM self-contact using tetrahedra |

Three parameters select the contact discretization per pair. Each accepts one of:

- **`"tet"`:** tetrahedralization-based contact. The default and the most accurate choice for most meshes.
- **`"vert"`:** vertex-based contact, preferable for very coarse meshes such as a single cube or tetrahedron.
- **`"none"`:** disable contact for that pair.

| Parameter | Default | Accepted values |
|---|---|---|
| `fem_floor_contact_type` | `"tet"` | `"tet"`, `"vert"`, `"none"` |
| `rigid_floor_contact_type` | `"tet"` | `"tet"`, `"vert"`, `"none"` |
| `rigid_rigid_contact_type` | `"tet"` | `"tet"`, `"none"` |

:::{note}
`rigid_rigid_contact_type` is declared to accept `"vert"`, but the solver only implements `"tet"` and `"none"`; passing `"vert"` raises. Use `"tet"` or `"none"` for rigid-rigid contact.
:::

## Grasping a deformable object

[`examples/sap_coupling/franka_grasp_fem_sphere.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/franka_grasp_fem_sphere.py) has a Franka arm grasp and lift an FEM sphere, the workload SAP is built for. A rigid-cube variant lives in [`franka_grasp_rigid_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/franka_grasp_rigid_cube.py).

A steady grasp demands tighter convergence than the defaults, because a loose solve lets the object creep out of the fingers over many steps. The example tightens both the PCG threshold and the SAP tolerances, and disables self-collision on the arm so the fingers can close fully:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1 / 60, substeps=2),
    rigid_options=gs.options.RigidOptions(enable_self_collision=False),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True, pcg_threshold=1e-10),
    coupler_options=gs.options.SAPCouplerOptions(
        pcg_threshold=1e-10,
        sap_convergence_atol=1e-10,
        sap_convergence_rtol=1e-10,
        linesearch_ftol=1e-10,
    ),
)
```

To hold a target vertex of an FEM body in place (a fixed constraint rather than a grasp), see [`fem_fixed_constraint.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sap_coupling/fem_fixed_constraint.py), which sets `FEMOptions(enable_vertex_constraints=True)` and drives a vertex with `set_vertex_constraints`.

## When to use SAP

- **Use SAP** for rigid-FEM manipulation of moderately deformable volumetric bodies, where you need stable, accurate contact under sustained load and can afford 64-bit precision.
- **Use the {doc}`IPC coupler <ipc_coupler>`** for cloth and highly deformable soft bodies.
- **Use the default coupler** ({doc}`Solvers and coupling </user_guide/theory/solvers_and_coupling>`) for scenes with MPM, SPH, or PBD, for rigid-only simulation, or when you need gradients for differentiable simulation.

## See also

- {doc}`IPC coupler <ipc_coupler>`: barrier-based contact for cloth and highly deformable bodies.
- {doc}`Solvers and coupling </user_guide/theory/solvers_and_coupling>`: how solvers and couplers fit together.
- {doc}`FEM options </api_reference/engine/solvers/fem_solver>` and {doc}`FEM elastic material </api_reference/engine/material/fem/elastic>`: configuring the deformable bodies SAP couples.
