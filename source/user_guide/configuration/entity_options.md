# Entity options

Every entity in a scene is built from **entity options**: one object that holds its morph, its surface, its material, and the settings its solver applies to it alone. This page explains how the class of those options picks the solver, how the material describes the physics independently of the solver, and how to give some links, geoms or vertices of an entity settings of their own.

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    fem_options=gs.options.FEMOptions(
        use_implicit_solver=True,
    ),
)
scene.add_entity(gs.morphs.Plane())
blob = scene.add_entity(
    options=gs.options.FEMEntityOptions(
        morph=gs.morphs.Sphere(
            pos=(0.0, 0.0, 0.5),
            radius=0.1,
        ),
        material=gs.materials.Elastic(
            youngs_modulus=1e5,
            poisson_ratio=0.45,
        ),
        solver_options=gs.options.FEMEntitySolverOptions(
            model="linear_corotated",
        ),
    ),
)
scene.build()
for _ in range(100):
    scene.step()
```

`blob` is an `FEMEntity`, because `FEMEntityOptions` names the FEM solver. The plane goes through the shorthand for rigid entities: passing a morph straight to `add_entity` builds a rigid entity, and the shorthand also takes a `material`, a `surface` and a few other arguments. Anything beyond them, such as the solver options or the options of some links, takes {py:class}`gs.options.RigidEntityOptions <genesis.options.entities.RigidEntityOptions>`.

## Walkthrough

### The options class picks the solver

We give each kind of entity its own options class: {py:class}`gs.options.RigidEntityOptions <genesis.options.entities.RigidEntityOptions>`, `KinematicEntityOptions`, `FEMEntityOptions`, `MPMEntityOptions`, `SPHEntityOptions`, the four `PBD*EntityOptions`, and `HybridEntityOptions`. The class decides which solver simulates the entity and which type `add_entity` returns, so the return type of `add_entity` follows from the options you pass. The {doc}`entity reference </api_reference/engine/entity/index>` lists each class next to the entity and the solver it selects.

The options are immutable once constructed, and the scene keeps its own copy as `entity.options`. Build a variant with `model_copy(update=...)` rather than editing one in place, and pass one options object to `add_entity` as many times as you need identical entities.

### The material describes the physics

A material states the physical law of the entity and its parameters, whichever solver simulates it. `gs.materials.Elastic` describes an elastic solid in Young's modulus and Poisson ratio, whether the FEM, MPM or PBD solver simulates it, and `gs.materials.Liquid` describes a fluid for the MPM, SPH and PBD solvers alike. A parameter you leave to None takes the default of the solver simulating the entity, and an options class raises an error on a material it does not accept or on a parameter its solver cannot honor. The {doc}`material reference </api_reference/options/material/index>` lists which options accept which material.

### Solver options hold the numerics

Settings that belong to how a solver integrates the entity rather than to what the entity is made of, such as the constitutive model of an FEM entity, the particle sampler of an MPM entity, or the coupling of a rigid entity with other solvers, live in the `solver_options` of the entity options. Each family has its own class, `FEMEntitySolverOptions` for `FEMEntityOptions` and so on, so a setting only appears where the solver supports it. Settings shared by every entity of a solver stay in the scene options, such as `gs.options.FEMOptions`; see {doc}`config_system`.

## Options for some links, geoms or vertices

A rigid entity can set options on some of its links and collision geoms, and an FEM entity on some of its vertices. Each scoped field takes a dictionary whose keys select the targets and whose values hold the options. These scoped options only expose settings the solver already holds at that granularity: the material of a geom, the coupling of a link, the pinning of a vertex.

### Links

Select links by name with {py:class}`gs.LinkIndex.named <genesis.options.indices.LinkIndex>`, or write the name, or a tuple of names, as the key. Each name is an exact link name or a glob pattern, so `"panda_finger*"` selects both fingers of a Franka, and a name that matches no link raises an error. `gs.LinkIndex.subtree("hand")` selects a link and every link below it in the kinematic tree, which is how to address a whole gripper without listing its links. This excerpt from [`examples/rigid/grasp_bottle.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/grasp_bottle.py) gives the finger pads of a Franka arm a grippy material, while the rest of the arm keeps the friction its asset states:

```python
franka = scene.add_entity(
    options=gs.options.RigidEntityOptions(
        morph=gs.morphs.MJCF(
            file="xml/franka_emika_panda/panda.xml",
        ),
        links={
            gs.LinkIndex.named("left_finger", "right_finger"): gs.options.LinkOptions(
                material=gs.materials.Material(
                    friction=1.5,
                ),
            ),
        },
    ),
)
```

{py:class}`gs.options.LinkOptions <genesis.options.entities.LinkOptions>` also takes `solver_options`, a {py:class}`gs.options.RigidLinkSolverOptions <genesis.options.entities.RigidLinkSolverOptions>` that couples some links with other solvers and leaves the rest out. The IPC examples use it to couple the fingers of a gripper alone; see {doc}`/user_guide/physics/coupling/ipc_coupler`. A link that the asset parser merges into its parent has no name of its own any more, so a selection naming it raises an error until you keep the link with the `links_to_keep` option of the morph.

### Geoms

Select collision geoms with {py:class}`gs.GeomIndex <genesis.options.indices.GeomIndex>`, by their ordinal within their link as the asset states them, or by the name the asset gives them: `gs.GeomIndex.at(0)` picks the first collision geom, `gs.GeomIndex.named("foot*")` the geoms whose names match the glob, and `gs.GeomIndex.all()` every one. MJCF assets name their geoms and USD assets name them by prim path, while URDF assets state no geom names. Geom options sit in the `geoms` field of `LinkOptions`, for the geoms of the selected links, or in the `geoms` field of `RigidEntityOptions`. The entity-level field takes `gs.GeomIndex.all()` and `gs.GeomIndex.named` for any morph, and ordinals only for a mesh or a primitive, whose entity has a single link. [`examples/rigid/link_and_geom_options.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/link_and_geom_options.py) gives the feet of a humanoid grippy geoms by name and makes its right leg denser through a subtree.

The ordinal counts the geoms as the asset states them, before Genesis World decomposes a mesh into convex pieces, so a geom option applies to every piece of the geom it selects.

### Vertices

Select vertices of an FEM entity with {py:class}`gs.VertexIndex <genesis.options.indices.VertexIndex>`: by ordinal with `at`, inside an axis-aligned box with `in_box`, or the vertex closest to a point with `closest_to`, all in the frame of the morph. Combine selections with `|`. This excerpt from [`examples/deformable/fem_hard_and_soft_constraint.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/deformable/fem_hard_and_soft_constraint.py) clamps a beam by its left end face:

```python
scene.add_entity(
    options=gs.options.FEMEntityOptions(
        morph=gs.morphs.Box(
            pos=SCENE_POS + np.array([0.3, -0.3, 0]),
            size=(0.4, 0.06, 0.06),
        ),
        material=gs.materials.Elastic(
            density=1000.0,
            youngs_modulus=1.0e5,
            poisson_ratio=0.45,
        ),
        solver_options=gs.options.FEMEntitySolverOptions(
            model="linear_corotated",
        ),
        vertices={
            gs.VertexIndex.in_box(lower=(-0.2, -0.03, -0.03), upper=(-0.2, 0.03, 0.03)): gs.options.VertexOptions(
                solver_options=gs.options.FEMVertexSolverOptions(
                    is_fixed=True,
                ),
            ),
        },
    ),
)
```

A fixed vertex stays at its initial position from the first substep on, as a hard constraint the FEM solver enforces. To move pinned vertices along a path or attach them to a rigid link instead, call `set_vertex_constraints` on the built entity.

### Precedence

A field set on a geom overrides the same field on its link, which overrides the entity, which overrides the value the asset states, which overrides the default of the solver. Fields you leave unset fall through to the next level, so a link material that sets `friction` alone keeps the density of the entity. Two selections of equal specificity that set the same field of the same target raise an error rather than letting the order of the dictionary decide, and two that set different fields both apply.

:::{note}
A density set on a link or a geom estimates the mass and the inertia of a link whose asset states none, or of every moving link under the `recompute_inertia` option of the morph. The rigid solver then simulates its body as unaligned, keeping the frame the asset authored. The IPC coupler rejects a scoped density on a link it simulates.
:::

## See also

- {doc}`/api_reference/engine/entity/index`: every entity options class and the entity it builds.
- {doc}`/api_reference/options/material/index`: the materials and the options that accept them.
- {doc}`/api_reference/options/selections`: `gs.LinkIndex`, `gs.GeomIndex` and `gs.VertexIndex`.
- {doc}`config_system`: the scene options and how they compose with the entity options.
