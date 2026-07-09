# Rigid collision: contacts and forces

Every simulation step, Genesis World finds which rigid bodies touch, generates a contact manifold for each touching pair, and hands those contacts to the constraint solver. This page explains how detection works conceptually and how to read the resulting contacts and contact forces back into Python. Force resolution (how contacts turn into accelerations) is covered in {doc}`rigid_constraint_model`.

The detection code lives under `genesis/engine/solvers/rigid/collider/`, driven by the collider's `detection()` method.

## How contacts are detected

Detection runs in two phases each step, from a cheap approximate cull to an exact contact manifold.

**Broad phase.** Each geometry gets a world-space axis-aligned bounding box (AABB), recomputed every step because rigid bodies move. A Sweep-and-Prune pass then reports only the geometry pairs whose boxes overlap, turning an all-pairs comparison into a near-linear one. The same pass drops pairs that cannot physically collide:

- **Adjacency:** two geometries on the same link, or on directly connected links.
- **Collision masks:** pairs excluded by their `contype` / `conaffinity` bitmasks.
- **Static pairs:** two geometries both fixed relative to the world.
- **Hibernation:** contacts between sleeping bodies, unless one side is awake.

**Narrow phase.** Each surviving pair is resolved to an exact contact manifold: a contact normal, a penetration depth, and one or more contact points. The algorithm depends on the geometry pair:

| Geometry pair | Path |
|---|---|
| General convex–convex, including plane–convex | Minkowski Portal Refinement (MPR) by default, or GJK with EPA when `use_gjk_collision=True`; a signed-distance-field query takes over on deep penetration. |
| Plane–box and box–box | Analytic special case, ported from MuJoCo for stability when a box lies flush on a plane. |
| Any geometry against height-field terrain | Terrain routine that can emit several contact points per supporting cell. |
| Non-convex meshes | Signed-distance-field sampling: vertices first (vertex–face), then edges (edge–edge), keeping the deepest penetration. |

MPR and GJK both operate through a *support function* ("which vertex lies farthest along a given direction?") so they run branch-free on the GPU without face-adjacency caches. GJK additionally reports a separation distance when the geometries are apart and is the differentiable path (it is selected automatically when the scene requires gradients). Both accelerate support queries with a precomputed support field; see {doc}`/user_guide/theory/support_field` for how that structure is built and used. To capture flush faces rather than a single point, Genesis perturbs the pose slightly around the first contact normal and gathers the extra contacts that result.

The number of candidate pairs the broad phase may emit is bounded by the `max_collision_pairs` option on {doc}`RigidOptions </api_reference/options/simulator_coupler_and_solver_options/rigid_options>`. Exceeding it at runtime halts the simulation, so raise it for scenes with dense contact.

## Reading contacts

Read the contacts from the most recent `scene.step()` with `get_contacts()` on any {doc}`rigid entity </api_reference/entity/rigid_entity/rigid_entity>`. It returns a dict of parallel arrays, one entry per contact that involves the entity.

```python
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene()
plane = scene.add_entity(gs.morphs.Plane())
ball = scene.add_entity(gs.morphs.Sphere(radius=0.2, pos=(0.0, 0.0, 0.5)))

scene.build()
for _ in range(200):
    scene.step()

contacts = ball.get_contacts()  # all contacts involving the ball
positions = contacts["position"]  # world-frame contact points, shape ([n_envs,] n_contacts, 3)
forces = contacts["force_a"]  # force on geom A, shape ([n_envs,] n_contacts, 3), N
```

Each entry shares a leading contact axis. Index and scalar fields have shape `([n_envs,] n_contacts)`; vector fields have shape `([n_envs,] n_contacts, 3)`. The fields are:

- **`geom_a`, `geom_b`:** global geometry indices of the two geometries in the pair. Recover a geometry with `scene.rigid_solver.geoms[idx]`.
- **`link_a`, `link_b`:** global link indices of the links owning those geometries, recoverable via `scene.rigid_solver.links[idx]`.
- **`position`:** contact point in the world frame, in meters.
- **`normal`:** contact normal, a world-space unit vector.
- **`penetration`:** penetration depth, positive when the geometries overlap.
- **`force_a`, `force_b`:** contact force on geometry A and on geometry B. They are equal and opposite, in newtons.
- **`valid_mask`:** present only when the scene is parallelized. See the note below.

To restrict the result to contacts against one other entity, pass `with_entity`. Passing the entity itself returns self-collisions only, and `exclude_self_contact=True` drops them:

```python
contacts = ball.get_contacts(with_entity=plane)  # only ball–plane contacts
```

:::{note}
With multiple environments, every field carries a leading `n_envs` axis and is padded to the largest contact count across environments, so the same array is rectangular. `valid_mask` (shape `(n_envs, n_contacts)`) marks which rows are real; filter with it before using the data. A single-environment scene returns the fields already trimmed, with no `valid_mask`.
:::

## Net contact force per link

When you only need the total external contact force on each link rather than the individual contact points, use `get_links_net_contact_force()`. It sums the contact forces the solver applied to every link of the entity:

```python
net = ball.get_links_net_contact_force()  # world frame, shape ([n_envs,] n_links, 3), N
```

This is the aggregate the constraint solver accumulated, so it reflects the resolved contact forces rather than the raw manifold. For a link resting on the ground, it balances gravity.

## When to use a contact sensor instead

`get_contacts()` and `get_links_net_contact_force()` pull the whole contact set on demand, which is convenient for scripting and debugging. For a per-link signal you sample every step in a control or training loop (with history, noise, and delay handled for you), attach a contact sensor instead. `ContactForce` reports the net force on a link in its own frame, and the tactile probes estimate dense per-taxel forces. See {doc}`/user_guide/sensing/contact`.

## See also

- {doc}`rigid_constraint_model`: how contacts, joint limits, and equality constraints are solved for the resulting motion.
- {doc}`/user_guide/theory/support_field`: the acceleration structure behind MPR and GJK support queries.
- {doc}`/user_guide/sensing/contact`: contact and tactile sensors for per-step readings.
