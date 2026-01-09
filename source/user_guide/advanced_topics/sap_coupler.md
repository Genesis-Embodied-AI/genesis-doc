# 🔧 SAP Coupler

Genesis provides Semi-Analytic Primal (SAP) coupling for accurate rigid-FEM contact handling.

## Requirements

```python
import genesis as gs

# Must use 64-bit precision
gs.init(backend=gs.gpu, precision="64")
```

## Basic Setup

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),  # Required
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_sap_iterations` | 5 | SAP solver iterations per step |
| `n_pcg_iterations` | 100 | Max PCG solver iterations |
| `sap_convergence_atol` | 1e-6 | Absolute tolerance |
| `sap_convergence_rtol` | 1e-5 | Relative tolerance |
| `sap_taud` | 0.1 | Dissipation time scale |
| `hydroelastic_stiffness` | 1e8 | Hydroelastic contact stiffness |
| `point_contact_stiffness` | 1e8 | Point contact stiffness |
| `enable_rigid_fem_contact` | True | Enable rigid-FEM coupling |

## Contact Type Options

| Parameter | Values | Description |
|-----------|--------|-------------|
| `fem_floor_contact_type` | "tet", "vert", "none" | FEM-floor contact method |
| `rigid_floor_contact_type` | "tet", "vert", "none" | Rigid-floor contact |
| `rigid_rigid_contact_type` | "tet", "none" | Rigid-rigid contact |

- **"tet"**: Default, tetrahedralization-based (most accurate)
- **"vert"**: For very coarse meshes
- **"none"**: Disable contact type

## Robot Grasping Example

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    rigid_options=gs.options.RigidOptions(enable_self_collision=False),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True, pcg_threshold=1e-10),
    coupler_options=gs.options.SAPCouplerOptions(
        pcg_threshold=1e-10,
        sap_convergence_atol=1e-10,
        sap_convergence_rtol=1e-10,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(radius=0.02, pos=(0.65, 0.0, 0.02)),
    material=gs.materials.FEM.Elastic(model="linear_corotated", E=1e5, nu=0.4),
)
```

## FEM Simulation

```python
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.0, 0.0, 0.1), radius=0.1),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4, model="linear_corotated"),
)
```

## When to Use SAP

**Use SAP for:**
- Rigid-FEM interactions (robot grasping deformables)
- Hydroelastic contact model
- High accuracy requirements
- Manipulation tasks with deformable objects

**Use LegacyCoupler for:**
- Multiple particle solvers (MPM, SPH, PBD)
- Differentiable simulation (SAP doesn't support gradients)
- Rigid-only simulations

## Performance

- **Faster convergence**: 40 steps vs 150 for LegacyCoupler
- **Higher accuracy**: Position error ~1e-3 vs ~5e-3
- **Trade-off**: Requires 64-bit precision, FEM implicit solver

## Limitations

- Only supports Rigid + FEM solvers
- Requires 64-bit precision (`precision="64"`)
- FEM must use implicit solver
- No gradient support for differentiable simulation
