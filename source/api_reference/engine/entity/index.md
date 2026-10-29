# Entity

An entity is a single simulated object in a Genesis World scene: a robot, a rigid body, a piece of cloth, a volume of fluid, or a deformable solid. It is the unit you add, configure, query, and control.

Create an entity by calling {py:meth}`scene.add_entity <genesis.engine.scene.Scene.add_entity>` with entity options. The class of the options decides the kind of entity and the solver simulating it, and its fields hold three ingredients:

- **Morph:** the geometry and pose: a primitive shape, a mesh, or a robot description loaded from URDF, MJCF, or USD. See {doc}`/api_reference/engine/entity/morph/index`.
- **Material:** the physical law the entity follows and its parameters, such as an elastic solid of a given stiffness. See {doc}`/api_reference/options/material/index`.
- **Surface:** the visual appearance used for rendering: color, texture, and visualization mode. See {doc}`/api_reference/engine/entity/surface/index`.

The options of each kind of entity add the settings of its solver specific to the entity (`solver_options`), and the options of a rigid or a deformable entity can set options on some of its links, geoms or vertices. For a worked example of adding an entity and stepping the scene, see {doc}`/user_guide/getting_started/hello_genesis`, and for the scoped options, see {doc}`/user_guide/configuration/entity_options`.

`add_entity` returns the entity object, whose type follows the options class: `gs.options.RigidEntityOptions` yields a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>`, `gs.options.MPMEntityOptions` an `MPMEntity`, and so on. Passing the morph, a `gs.materials.Material` and the surface directly to `add_entity`, without options, builds a rigid entity. You interact with an entity through its own methods, whose return tensors follow the batched-optional shape convention; see {doc}`/user_guide/configuration/conventions`.

## Entity types

Each kind of entity has its own options class, which selects the solver and therefore the type of the returned entity.

| Entity options | Entity | Solver | Use |
|---|---|---|---|
| `RigidEntityOptions` | `RigidEntity`, `DroneEntity`, `TerrainEntity` | Rigid | Articulated rigid bodies and robots; the morph selects a drone or a terrain |
| `KinematicEntityOptions` | `KinematicEntity` | Kinematic | Ghost or reference entities, moved by script and rendered, without physics |
| `FEMEntityOptions` | `FEMEntity` | Finite Element Method (FEM) | Deformable solids on tetrahedral meshes, and cloth under the IPC coupler |
| `MPMEntityOptions` | `MPMEntity` | Material Point Method (MPM) | Elastic and plastic solids, sand, snow, and liquids |
| `SPHEntityOptions` | `SPHEntity` | Smoothed Particle Hydrodynamics (SPH) | Liquids |
| `PBDClothEntityOptions` | `PBD2DEntity` | Position Based Dynamics (PBD) | Cloth |
| `PBDElasticEntityOptions` | `PBD3DEntity` | PBD | Elastic volumes |
| `PBDLiquidEntityOptions` | `PBDParticleEntity` | PBD | Liquids |
| `PBDParticleEntityOptions` | `PBDFreeParticleEntity` | PBD | Particles that ignore each other, for effects |
| `HybridEntityOptions` | `HybridEntity` | Rigid and a soft solver | A soft skin actuated by a rigid skeleton |

An **`Emitter`**, added with `scene.add_emitter`, injects the particles of an MPM, SPH or PBD liquid or particle entity into the scene during simulation, for spraying and streaming effects.

## Options

```{eval-rst}
.. autoclass:: genesis.options.entities.EntityOptions
```

```{toctree}
:titlesonly:

rigid_entity/index
kinematic_entity
mpm_entity
fem_entity
pbd_entity/index
sph_entity
drone_entity
terrain_entity
hybrid_entity
emitter
```

## Building blocks

The morph (geometry and pose) and the surface (appearance, with textures supplying per-point surface values) passed to `add_entity` each have their own reference below. The material lives under {doc}`/api_reference/options/material/index`.

```{toctree}
:titlesonly:

morph/index
surface/index
texture/index
```
