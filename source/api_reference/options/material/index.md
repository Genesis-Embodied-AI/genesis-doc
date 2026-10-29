# Material

A material states the physical law of an entity and the parameters of that law: its density, its stiffness, its yield behavior. The entity options class decides which solver simulates the entity, and the material describes what the entity is made of, so the same `gs.materials.Elastic` describes an elastic solid whether the FEM, MPM or PBD solver simulates it. A parameter left to None takes the default of the solver simulating the entity, and the entity options raise an error on a parameter their solver cannot honor.

Materials live under `gs.materials`, one class per law. This table lists the entity options that accept each one:

| Material | Law | Entity options |
|---|---|---|
| `gs.materials.Material` | Rigid body | `RigidEntityOptions`, and its `LinkOptions` and `GeomOptions` |
| `gs.materials.Elastic` | Elastic solid | `FEMEntityOptions`, `MPMEntityOptions`, `PBDElasticEntityOptions` |
| `gs.materials.Cloth` | Thin elastic sheet | `FEMEntityOptions` (IPC coupler), `PBDClothEntityOptions` |
| `gs.materials.ElastoPlastic` | Solid with a yield limit | `MPMEntityOptions` |
| `gs.materials.Liquid` | Fluid | `MPMEntityOptions`, `SPHEntityOptions`, `PBDLiquidEntityOptions`, `PBDParticleEntityOptions` |
| `gs.materials.Sand` | Granular medium | `MPMEntityOptions` |
| `gs.materials.Snow` | Compacting solid | `MPMEntityOptions` |
| `gs.materials.Muscle` | Actuated elastic solid | `FEMEntityOptions`, `MPMEntityOptions` |

Kinematic entities take no material, and a hybrid entity takes one material for each of its two parts. For the modeling background behind the deformable laws, including which solver suits which phenomenon, see {doc}`/user_guide/theory/soft_solvers`.

```{eval-rst}
.. autoclass:: genesis.options.materials.BaseMaterial
```

```{toctree}
:titlesonly:

material
elastic
cloth
elasto_plastic
liquid
sand
snow
muscle
```
