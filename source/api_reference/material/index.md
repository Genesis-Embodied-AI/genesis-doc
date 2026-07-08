# Material

A material assigns an entity to a physics solver and configures the constitutive model that governs how the entity deforms and responds to forces. When you call `scene.add_entity`, the `material` argument decides whether the entity is simulated as a rigid body, a deformable solid, a cloth, a granular medium, or a fluid, and it holds the physical parameters for that model — stiffness, density, yield behavior, and so on.

Materials live under `gs.materials`. Each family maps to one solver, and the class within the family selects the constitutive model:

| Family | Solver | Materials |
|---|---|---|
| `gs.materials.Rigid` | Rigid body | `Rigid` |
| `gs.materials.MPM.*` | Material Point Method | `Elastic`, `ElastoPlastic`, `Liquid`, `Muscle`, `Sand`, `Snow` |
| `gs.materials.FEM.*` | Finite Element Method | `Cloth`, `Elastic`, `Muscle` |
| `gs.materials.PBD.*` | Position Based Dynamics | `Cloth`, `Elastic`, `Liquid`, `Particle` |
| `gs.materials.SPH.*` | Smoothed Particle Hydrodynamics | `Liquid` |
| `gs.materials.SF.*` | Stable Fluid | `Smoke` |
| `gs.materials.Hybrid` | Rigid + deformable coupling | `Hybrid` |
| `gs.materials.Tool` | Kinematic collider coupling | `Tool` |
| `gs.materials.Kinematic` | None (visualization only) | `Kinematic` |

`gs.materials.Hybrid` is not a solver of its own — it couples a rigid material and a soft material to simulate a soft skin actuated by an inner rigid skeleton.

For the modeling background behind the deformable families, including which solver suits which phenomenon, see {doc}`/user_guide/advanced_topics/nonrigid_models`.

```{toctree}
rigid
mpm/index
fem/index
pbd/index
sph/index
sf/index
hybrid
tool
kinematic
```
