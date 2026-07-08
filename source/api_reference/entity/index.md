# Entity

An entity is a single simulated object in a Genesis World scene — a robot, a rigid body, a piece of cloth, a volume of fluid, or a deformable solid. It is the unit you add, configure, query, and control.

You create an entity by calling {py:meth}`scene.add_entity <genesis.engine.scene.Scene.add_entity>`, which combines three ingredients:

- **Morph:** the geometry and pose — a primitive shape, a mesh, or a robot description loaded from URDF, MJCF, or USD. See {doc}`/api_reference/options/morph/index`.
- **Material:** the physical model that decides which solver simulates the entity and how it responds to forces. See {doc}`/api_reference/material/index`.
- **Surface:** the visual appearance used for rendering — color, texture, and visualization mode. See {doc}`/api_reference/options/surface/index`.

```python
import genesis as gs

gs.init()
scene = gs.Scene()

franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)

scene.build()  # required before stepping or reading state
```

`add_entity` returns the entity object. Its concrete type depends on the material's solver: a rigid material yields a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>`, an MPM material yields an `MPMEntity`, and so on.

## Object-oriented accessors

Genesis World follows an object-oriented model: you interact with each entity through methods on the object `add_entity` returned, rather than through global scene calls indexed by id. After {py:meth}`scene.build() <genesis.engine.scene.Scene.build>`, you read state and issue commands directly — for example `franka.get_pos()`, `franka.get_dofs_position()`, and `franka.control_dofs_position(...)` on a rigid entity. The available methods differ by entity type; see each type's reference page.

State-reading methods return tensors that follow the batched-optional shape convention: the leading environment dimension is present when the scene is built with multiple environments and absent otherwise, for example `([n_envs,] 3)` for a position. See {doc}`/user_guide/getting_started/hello_genesis` for a worked example.

## Entity types

Each physics solver has its own entity type. Choosing a material selects the solver, and therefore the type of the returned entity.

- **`RigidEntity`:** articulated rigid bodies and robots simulated by the rigid solver. It is the type used for most manipulation and locomotion tasks and exposes links, joints, and dofs.
- **`DroneEntity`:** a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>` subclass that adds propeller and thrust control for quadrotor simulation.
- **`MPMEntity`:** elastic and plastic solids, sand, snow, and similar continua simulated with the Material Point Method (MPM) solver.
- **`FEMEntity`:** deformable solids simulated with the Finite Element Method (FEM) solver.
- **PBD entities:** cloth, ropes, and particle-based fluids simulated by the Position Based Dynamics (PBD) solver. The material determines the concrete type — for example `PBD2DEntity` for cloth and `PBD3DEntity` for elastic volumes.
- **`SPHEntity`:** liquids and gases simulated with the Smoothed Particle Hydrodynamics (SPH) solver.
- **`HybridEntity`:** an entity composed of both rigid and soft components, used to couple, for example, a soft body to a rigid skeleton.
- **`Emitter`:** a helper that continuously injects particles into a particle-based entity during simulation, for spraying and streaming effects.

```{toctree}
rigid_entity/index
mpm_entity
fem_entity
pbd_entity/index
sph_entity
drone_entity
hybrid_entity
emitter
```
