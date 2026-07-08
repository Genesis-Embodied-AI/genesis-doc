# Naming and indexing conventions

Genesis World uses a small, consistent set of naming rules across its API and its source. This page is the reference for three of them: how an entity is identified (`name`, `uid`, `idx`), how indices switch between an entity's own numbering and the solver's global numbering (`*_idx_local` vs `*_idx`), and the `i_*` loop-variable and field-naming conventions you will meet when reading solver code.

Two conventions in one sentence: identifiers answer "which entity is this," and indices answer "which slot in a state array." They are unrelated numbering systems, and mixing them is the most common source of off-by-entity bugs.

## Identifying an entity: name, uid, and idx

Every entity carries three identifiers, each for a different job:

- **`name`:** a human-readable string. You pass it to `scene.add_entity(..., name=...)`, or Genesis World generates one from the morph type and a UID prefix. Names are how you look an entity up later.
- **`uid`:** a globally unique ID assigned at creation. It never collides across entities and is stable for the life of the object. Its `short()` form (a 7-character prefix) is what appears in terminal logs.
- **`idx`:** the entity's integer position in the scene's creation order. This is an *index*, not an identifier you should hand-write. It exists so the engine can address the entity's data.

The naming tutorial [`examples/tutorials/entity_name.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/entity_name.py) shows all three in use. Look up an entity by name or by short UID:

```python
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5), size=(0.2, 0.2, 0.2)))
ground = scene.add_entity(gs.morphs.Plane(), name="ground")

scene.get_entity(name="ground")        # exact-name lookup
scene.get_entity(uid=box.uid.short())  # short-UID lookup (substring of the full uid)

scene.entity_names  # tuple of every entity's name, in creation order
```

Prefer `name` for lookups you write by hand, and reserve `uid` for disambiguating entities that share a generated name. The same `name` / `uid` pair identifies links and joints within a rigid entity. `entity.get_link(name=...)` and `entity.get_joint(name=...)` work the same way.

| Identifier | Type | Assigned by | Use it to |
|---|---|---|---|
| `name` | `str` | you, or auto-generated | look an entity up in a scene |
| `uid` | UID object | Genesis World, at creation | disambiguate; read from logs via `uid.short()` |
| `idx` | `int` | Genesis World, at creation | address the entity's data (rarely written by hand) |

## Local and global indices

A rigid solver stores the state of *every* entity in flat, shared arrays: one row per **dof** (degree of freedom), one per link, one per configuration variable `q`, and so on. So there are two ways to number the same dof:

- **Global index (`*_idx`):** the dof's absolute row in the solver's arrays, counting across all entities. A two-armed scene numbers the second arm's dofs after the first arm's.
- **Local index (`*_idx_local`):** the dof's position *within its own entity*, always starting at zero. The first dof of any entity is local index `0`, regardless of what was added before it.

The two differ by a per-entity offset. For dofs it is `entity.dof_start`; the entity also exposes `link_start` and `q_start` for the link and `q` arrays. A joint's `dofs_idx` (global) and `dofs_idx_local` (local) properties are defined by exactly this shift:

```python
# genesis/engine/entities/rigid_entity/rigid_joint.py
dofs_idx       = list(range(dof_start, dof_end))
dofs_idx_local = list(range(dof_start - entity.dof_start, dof_end - entity.dof_start))
```

Because local indices are stable no matter how many other entities share the scene, they are what you build control targets from. The control tutorial [`examples/tutorials/control_your_robot.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/control_your_robot.py) reads a Franka's motor dofs by joint name, then addresses them locally:

```python
motors_dof_idx = [franka.get_joint(name).dofs_idx_local[0] for name in joints_name]

franka.set_dofs_kp(
    kp=np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local=motors_dof_idx,
)
```

## How indices appear in the API

Entity methods that read or write batched state take a *local* selector and translate it to global indices internally, through `RigidEntity._get_global_idx`, before calling the solver. The argument is named `*_idx_local` to make the numbering explicit at the call site:

```python
franka.set_dofs_position(position, dofs_idx_local=motors_dof_idx)
franka.get_links_pos(links_idx_local=[0, 1])
franka.set_qpos(qpos, qs_idx_local=...)
```

- **Entity methods take local indices.** `dofs_idx_local`, `links_idx_local`, `qs_idx_local`. Passing `None` selects the entity's full range.
- **Solver methods take global indices.** The `RigidSolver` equivalents accept already-resolved `dofs_idx`, `links_idx`, and so on. Reach for them only when you are working across entities at the solver level.
- **`envs_idx` has no local form.** Environment (**env**) selection is scene-wide, so batched methods take a single `envs_idx` that indexes environments directly. See {doc}`parallel simulation </user_guide/getting_started/parallel_simulation>` for how the batch dimension works.

:::{note}
The properties named without a suffix (a joint's `dof_start`, a link's `idx`, an entity's `idx`) are global. The `_local` suffix is only ever added to opt *into* entity-relative numbering. When in doubt, an index is global.
:::

## Field and loop-variable naming in the source

The conventions above surface names you also see when reading solver code. If you only use the public API, you can stop here; the rest is a map for the source under [`genesis/engine/solvers/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/genesis/engine/solvers).

**Data fields follow `<representation>_<computation-type>`.** The representation is always plural (`dofs`, `links`, `particles`, `elements`), and the computation-type suffix marks how the field is used:

- **`*_state`:** dynamic state updated every solver step (for example `dofs_state`, `links_state`).
- **`*_info`:** static properties fixed for the simulation, such as mass or stiffness (`dofs_info`, `geom_info`).
- **`*_render`:** fields consumed only by visualization, never by physics (`particles_render`).
- **`*_ng`:** a state variant with `requires_grad` disabled (`particles_state_ng`); `*_reordered` marks a spatially reordered cache.

**Loop indices are `i_<representation-initial>`.** Kernels iterate flat arrays with short names whose letter names the thing being indexed. These are the global indices described above, not local ones:

| Variable | Indexes |
|---|---|
| `i_b` | batch: the environment |
| `i_e` | entity |
| `i_l` | link |
| `i_j` | joint |
| `i_d` | dof |
| `i_g` | geometry (`i_ga`, `i_gb` for the two geometries in a collision pair) |
| `i_v` | vertex |

For the concrete field layouts of each solver (the full state and info structs), read the solver files themselves, starting from [`rigid_solver.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/genesis/engine/solvers/rigid/rigid_solver.py) and the entity classes under [`genesis/engine/entities/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/genesis/engine/entities).

## See also

- {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>`: where `name` and entities are first introduced.
- {doc}`Control your robot </user_guide/getting_started/control_your_robot>`: local dof indices in a full control loop.
- {doc}`RigidJoint API </api_reference/entity/rigid_entity/rigid_joint>` and {doc}`RigidEntity API </api_reference/entity/rigid_entity/rigid_entity>`: the `dofs_idx` / `dofs_idx_local` properties and the `*_idx_local` methods.
