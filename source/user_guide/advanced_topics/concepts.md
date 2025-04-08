# 🧩 Concepts

## Systematic Overview

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

## Data Structure of Rigid Entities
