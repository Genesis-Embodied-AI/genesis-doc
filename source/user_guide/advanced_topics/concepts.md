# 🧩 Concepts

## Systemat Architecture Overview

```{figure} ../../_static/images/overview.png
```

<!-- From an user perspective, building an environment using Genesis is to add `Entity` in `Scene`, where `Entity` is specified by
- `Morph`: the geometry of the entity, e.g., primitive shapes or URDF.
- `Material`: the material of the entity, e.g., elastic object, liquid, sand, etc. Material is associated with the underlying solvers, e.g., there is MPM liquid and SPH liquid, those demonstrate different behaviors.
- `Surface`: the texture, rendering surface parameters etc

Under the hood, the scene consists of a simulator that encapsulates,
- `Solver`: the physics solver that handles the core physics engine with different methods like rigid, material point method (MPM), finite element method (FEM), etc.
- `Coupler`: the bridge across solvers that handle forces and any interaction in between. -->

From a user’s perspective, building an environment in Genesis involves adding `Entity` objects to a `Scene`. Each `Entity` is defined by:
- `Morph`: the geometry of the entity, such as primitive shapes (e.g., cube, sphere) or articulated models (e.g., URDF, MJCF).
- `Material`: the physical properties of the entity, such as elastic solids, liquids, or granular materials. The material type determines the underlying solver used—for example, both MPM and SPH can simulate liquids, but each exhibits different behaviors.
- `Surface`: the visual and interaction-related surface properties, such as texture, roughness, or reflectivity.

Behind the scenes, the `Scene` is powered by a `Simulator`, which includes:
- `Solver`: the core physics solvers responsible for simulating different physical models, such as rigid body dynamics, Material Point Method (MPM), Finite Element Method (FEM), Position-Based Dynamics (PBD), and Smoothed Particle Hydrodynamics (SPH).
- `Coupler`: a module that handles interactions between solvers, ensuring consistent force coupling and inter-entity dynamics.


## Data Indexing

We have been recieving a lot of questions about how to partially manipulate a rigid entity like only controling or retrieving certain attributes. Thus, we figure it would be nice to write a more in-depth explaination on index access to data.

**Structured Data Field**. For most of the case, we are using [struct Taichi field](https://docs.taichi-lang.org/docs/type#struct-types-and-dataclass). Take MPM for an example for better illustration ([here](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L103C1-L107C10) and [here](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/solvers/mpm_solver.py#L123)),
```
struct_particle_state_render = ti.types.struct(
    pos=gs.ti_vec3,
    vel=gs.ti_vec3,
    active=gs.ti_int,
)
...
self.particles_render = struct_particle_state_render.field(
    shape=self._n_particles, needs_grad=False, layout=ti.Layout.SOA
)
```
This means we are create a huge "array" (called field in Taichi) with each entry being a structured data type that includes `pos`, `vel`, and `active`. Note that this data field is of length `n_particles`, which include __ALL__ particles in a scene. Then, suppose there are multiple entities in the scene, how do we differentiate across entities? A straightforward idea is to "tag" each entry of the data field with the corresponding entity ID. However, it may not be the best practice from the memory layout, computation, and I/O perspective. Alternatively, we use index offsets to distinguish entities.

**Local and Global Indexing**. The index offset provides simultaneously the simple, intuitive user interface (local indexing) and the optimized low-level implementation (global indexing). Local indexing allows interfacing __WITHIN__ an entity, e.g., the 1st joint or 30th particles of a specific entity. The global indexing is the pointer directly to the data field inside the solver which consider all entities in the scene. A visual illustration looks like this

```{figure} ../../_static/images/local_global_indexing.png
```

We provide some concrete examples in the following for better understanding,
- In MPM simulation, suppose `vel=torch.zeros((mpm_entity.n_particles, 3))` (which only considers all particles of __this__ entity), [`mpm_entity.set_velocity(vel)`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L296) automatically abstract out the offseting for global indexing. Under the hood, Genesis is actually doing something conceptually like `mpm_solver.particles[start:end].vel = vel`, where `start` is the offset ([`mpm_entity.particle_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L453)) and `end` is the offset plus the number of particles ([`mpm_entity.particle_end`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/particle_entity.py#L457)).
- In rigid body simulation, all `*_idx_local` mean the local indexing, with which the users interact. They will be converted to the global indexing through `entity.*_start + *_idx_local`. Suppose we want to get the 3rd dof position by [`rigid_entity.get_dofs_position(dofs_idx_local=[2])`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2201), this is actually accessing `rigid_solver.dofs_state[2+offset].pos` where `offset` is [`rigid_entity.dofs_start`](https://github.com/Genesis-Embodied-AI/Genesis/blob/53b475f49c025906a359bc8aff1270a3c8a1d4a8/genesis/engine/entities/rigid_entity/rigid_entity.py#L2717).

(An interesting read of a relevant design pattern called [entity component system (ECS)](https://en.wikipedia.org/wiki/Entity_component_system))

## Direct Access to Data Field

Normally, we do not encourage users to directly access the (Taichi) data field.
Instead, users should mostly use the APIs in each entity, such as `RigidEntity.get_dofs_position`.
However, if one would like to access to data field not supported via APIs and could not wait for the new API support, one could try a direct access of data field, which may be a quick and dirty (yet most likely inefficient) solution. Specifically, following the data indexing mechanism described in the previous section, suppose one would like to do
```
entity: RigidEntity = ...
tgt = entity.get_dofs_position(...)
```

This is equivalent to
```
all_dofs_pos = entity.solver.dofs_state.pos.to_torch()
tgt = all_dofs_pos[:, entity.dof_start:entity.dof_end]  # the first dimension is the batch dimension
```

All entities are associated with a specific solver (except for hybrid entity).
Each desired physical attribute is stored somewhere in the solver (e.g., dofs position here is stored as `dofs_state.pos` in the rigid solver).
For more details of these mapping, you could check {doc}`Naming and Variables <naming_and_variables>`. 
Also, all the data field in the solver follows a global indexing (for all entities) where you need `entity.*_start` and `entity.*_end` to only extract the data relevant with a specific entity.

