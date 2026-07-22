# Entity

An entity is a single simulated object in a Genesis World scene: a robot, a rigid body, a piece of cloth, a volume of fluid, or a deformable solid. It is the unit you add, configure, query, and control.

You create an entity by calling {py:meth}`scene.add_entity <genesis.engine.scene.Scene.add_entity>`, which combines three ingredients:

- **Morph:** the geometry and pose: a primitive shape, a mesh, or a robot description loaded from URDF, MJCF, or USD. See {doc}`/api_reference/engine/entity/morph/index`.
- **Material:** the physical model that decides which solver simulates the entity and how it responds to forces. See {doc}`/api_reference/engine/material/index`.
- **Surface:** the visual appearance used for rendering: color, texture, and visualization mode. See {doc}`/api_reference/engine/entity/surface/index`.

For a worked example of adding an entity and stepping the scene, see {doc}`/user_guide/getting_started/hello_genesis`.

`add_entity` returns the entity object. Its concrete type depends on the material's solver: a rigid material yields a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>`, an MPM material yields an `MPMEntity`, and so on. You interact with an entity through its own methods, whose return tensors follow the batched-optional shape convention; see {doc}`/user_guide/getting_started/hello_genesis`.

## Entity types

Each physics solver has its own entity type. Choosing a material selects the solver, and therefore the type of the returned entity.

- **`RigidEntity`:** articulated rigid bodies and robots simulated by the rigid solver. It is the type used for most manipulation and locomotion tasks and exposes links, joints, and dofs.
- **`DroneEntity`:** a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>` subclass that adds propeller and thrust control for quadrotor simulation.
- **`MPMEntity`:** elastic and plastic solids, sand, snow, and similar continua simulated with the Material Point Method (MPM) solver.
- **`FEMEntity`:** deformable solids simulated with the Finite Element Method (FEM) solver.
- **PBD entities:** cloth, ropes, and particle-based fluids simulated by the Position Based Dynamics (PBD) solver. The material determines the concrete type: for example `PBD2DEntity` for cloth and `PBD3DEntity` for elastic volumes.
- **`SPHEntity`:** liquids and gases simulated with the Smoothed Particle Hydrodynamics (SPH) solver.
- **`SFParticleEntity`:** smoke and gaseous media simulated with the Stable Fluid (SF) solver.
- **`ToolEntity`:** a kinematically-scripted collider that couples one-way with soft and particle-based entities to push or deform them.
- **`HybridEntity`:** an entity composed of both rigid and soft components, used to couple, for example, a soft body to a rigid skeleton.
- **`Emitter`:** a helper that continuously injects particles into a particle-based entity during simulation, for spraying and streaming effects.

```{toctree}
:titlesonly:

rigid_entity/index
mpm_entity
fem_entity
pbd_entity/index
sph_entity
sf_entity
drone_entity
hybrid_entity
tool_entity
emitter
```

## Building blocks

The morph (geometry and pose) and the surface (appearance, with textures supplying per-point surface values) passed to `add_entity` each have their own reference. The material (physical model and solver) is documented under {doc}`/api_reference/engine/material/index`.

```{toctree}
:titlesonly:

morph/index
surface/index
texture/index
```
