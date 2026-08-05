# Collision detection

The second layer of a step finds which rigid bodies touch, generates a contact manifold for each touching pair, and hands those contacts to the constraint solver. This page covers how detection works, how to read the resulting contacts back into Python, and the support field the convex algorithms rest on. Turning contacts into accelerations is covered in {doc}`constraints`.

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
| Plane–box and box–box | Analytic special case, for stability when a box lies flush on a plane. |
| Any geometry against height-field terrain | Terrain routine that can emit several contact points per supporting cell. |
| Non-convex meshes | Signed-distance-field sampling: vertices first (vertex–face), then edges (edge–edge), keeping the deepest penetration. |

MPR and GJK both operate through a *support function* ("which vertex lies farthest along a given direction?") so they run branch-free on the GPU without face-adjacency caches. GJK additionally reports a separation distance when the geometries are apart and is the differentiable path (it is selected automatically when the scene requires gradients). Both accelerate support queries with a precomputed support field, described [below](#support-functions). To capture flush faces rather than a single point, Genesis perturbs the pose slightly around the first contact normal and gathers the extra contacts that result. GJK is the more stable of the two and much the slower, so we default to MPR and turn GJK on automatically when the scene requires gradients.

The number of candidate pairs the broad phase may emit is bounded by the `max_collision_pairs` option on {doc}`RigidOptions </api_reference/engine/solvers/rigid_solver>`. Exceeding it at runtime halts the simulation, so raise it for scenes with dense contact.

## Reading contacts

Read the contacts from the most recent `scene.step()` with `get_contacts()` on any {doc}`rigid entity </api_reference/engine/entity/rigid_entity/rigid_entity>`. It returns a dict of parallel arrays, one entry per contact that involves the entity.

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
contacts = ball.get_contacts(with_entity=plane)  # only ball-plane contacts
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

`get_contacts()` and `get_links_net_contact_force()` pull the whole contact set on demand, which is convenient for scripting and debugging. For a per-link signal you sample every step in a control or training loop (with history, noise, and delay handled for you), attach a contact sensor instead. {py:class}`ContactForce <genesis.options.sensors.options.ContactForce>` reports the net force on a link in its own frame, and the tactile probes estimate dense per-taxel forces. See {doc}`/user_guide/sensing/contact`.

## Support functions

For a convex shape $S$ and a query direction $d$, the **support function** returns the point of $S$ that maximizes the projection onto $d$:

$$
s_S(d) = \arg\max_{x \in S} \; x \cdot d
$$

Geometrically, $s_S(d)$ is the point you reach by sliding a plane with normal $d$ inward from infinity until it first touches the shape: the shape's extreme point along $d$.

This single primitive is enough to drive the two narrow-phase algorithms Genesis uses:

- **GJK (Gilbert–Johnson–Keerthi):** determines whether two shapes intersect, and finds the closest points when they don't, by exploring the Minkowski difference $A \ominus B$ purely through support queries.
- **MPR (Minkowski Portal Refinement):** finds a penetration direction and depth for overlapping shapes, again evaluating only support points.

Both operate on the Minkowski difference, whose support function decomposes into one query per shape:

$$
s_{A \ominus B}(d) = s_A(d) - s_B(-d)
$$

Because neither algorithm inspects faces or edges, a shape only needs to answer support queries to participate in collision detection. The support function, not the mesh, is the interface a shape must provide.

Each support query is dispatched by geometry type:

| Geometry | How the extreme point is computed |
|---|---|
| Sphere | Center offset by the radius along $d$. |
| Ellipsoid | Closed form from the direction in the local frame. |
| Capsule | Endpoint selected by the sign of $d$ along the axis, offset by the radius. |
| Cylinder | Rim point of the cap selected along the axis. |
| Box | Corner chosen by the sign of $d$ in each local axis. |
| Terrain | Extreme vertex of the active prism cell. |
| Convex mesh | Table lookup into the precomputed support field. |

Primitives have analytical support functions: the extreme point follows directly from a formula, so no search is needed. A general convex mesh has no such formula. The naive answer is to project every vertex onto $d$ and take the maximum, which costs $O(N)$ per query for a mesh of $N$ vertices, and both GJK and MPR issue many queries per contact pair, per step. The support field exists to remove that cost.

## Support field

Only convex meshes use the field. It precomputes the answer for a dense set of directions once, then answers any query by table lookup. The collider builds it when the scene is built.

### Precomputation

The unit sphere of directions is sampled on a regular latitude–longitude grid of `support_res × support_res` cells. The default resolution is `support_res = 180`, giving $180 \times 180 = 32{,}400$ sample directions. Cell $(i, j)$ maps to angles

$$
\theta = \frac{i}{\text{res}}\,2\pi - \pi \in [-\pi, \pi), \qquad
\phi = \frac{j}{\text{res}}\,\pi \in [0, \pi),
$$

and to the direction $d = (\sin\phi\cos\theta,\; \sin\phi\sin\theta,\; \cos\phi)$, with angles in radians.

For each geometry, Genesis projects all of its vertices onto every sample direction and records the winning vertex: its position in the mesh's local frame and its index. The results for all geometries are packed into flat arrays, so a single query needs no host round-trip.

### Query

A query rotates the world-space direction into the mesh's local frame, looks up the precomputed vertex, and transforms it back to world space. The lookup inverts the grid mapping (`theta = atan2(d_y, d_x)`, `phi = acos(d_z)`) to find the continuous cell coordinates, then evaluates the four cells bracketing them (`floor` and `ceil` of each coordinate) and keeps the vertex with the largest dot product. This is a fixed, four-cell search regardless of mesh size, so the query is $O(1)$ in the vertex count.

The four-cell neighborhood also lets the field report how many distinct vertices tie for the maximum. GJK uses that count to detect directions where the support point is ambiguous and perturb the query, which keeps the algorithm numerically stable on flat faces and shared edges.

### Data layout

The field is stored as a struct of flat arrays in a Quadrants-resident structure so collision kernels read it without pointer chasing. Per-geometry blocks are concatenated and indexed through a prefix-sum offset.

| Field | Shape | Description |
|---|---|---|
| `support_v` | `(n_support_cells, 3)` | Winning vertex positions, in each geometry's local frame. |
| `support_vid` | `(n_support_cells,)` | Corresponding vertex index in the original mesh. |
| `support_cell_start` | `(n_geoms,)` | Offset of each geometry's block into the flattened arrays. |

At the default resolution, each convex mesh contributes $32{,}400$ cells. At single precision (three floats plus one integer per cell) that is roughly 0.5 MB per mesh, independent of the mesh's vertex count.

### Trade-offs

- **Constant-time lookups:** a query is a fixed four-cell search rather than a scan over vertices, which also means fewer diverging branches on the GPU.
- **Uniform representation:** every convex mesh reduces to the same struct-of-arrays layout, with no per-shape bounding volume or hierarchy to build or traverse.
- **Approximate, not exact:** the grid has a fixed angular resolution, so a query direction snaps to the nearest sampled cells. A feature narrower than one angular cell may return a neighboring vertex rather than the true extreme point.
- **Fixed preprocessing cost:** the field is built for every geometry at scene build time and stored at full resolution, so both build time and memory grow with the number of geometries in the scene.

:::{note}
When MuJoCo compatibility is enabled, a mesh query falls back to an exhaustive vertex scan for bit-level agreement with MuJoCo.
:::

## Contact islands and hibernation

The solver partitions links into **contact islands**: connected components of a coupling graph whose edges are kinematic (every link to its parent), contacts, and equality constraints. An articulated body stays one island; an entity holding several free bodies splits into one island per body. Each island is an exactly decoupled block of the constraint solve, so `use_contact_island` (default `True`) lets the solver factor and solve them separately. It has no effect on a scene that is already one coupled tree, or on a differentiable scene, which uses the dense whole-scene solve regardless.

**Hibernation** extends that partition in time. Each step, every awake link's maximum degree-of-freedom (dof) speed is compared against `hibernation_thresh_vel`. Each dof velocity is weighted by its `dof_length`, which is 1 for a translational dof and the swept radius for a rotational one, so a single linear tolerance covers both and the rotational jitter of a small body no longer keeps it awake. A link that stays under the tolerance for 10 consecutive steps is ready to sleep, and an island hibernates once all of its links are ready, at which point their dof velocities are zeroed. Two things wake an island again: a new contact against one of its bodies, resolved before the solve so the body responds the same step, and a coupling force arriving from another solver.

A sleeping island is skipped by the solve and by the broad phase. In a scene with many settled bodies, per-step cost then follows the number of *awake* bodies rather than the total.

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        use_hibernation=True,
    ),
)
```

Hibernation is entirely automatic, driven by two options rather than by any call you make. `use_hibernation` defaults to `False`, and `hibernation_thresh_vel` is the speed below which a link may sleep, in m/s, defaulting to `1e-4` under MuJoCo compatibility and `2e-3` otherwise.

:::{note}
The gain is largest on the CPU backend, where skipping sleeping islands raises the serial step rate directly, and it pairs with `performance_mode=True`. Hibernation is unavailable in differentiable scenes, which fall back to the dense whole-scene solve.
:::

Read which links are asleep from the solver state:

```python
from genesis.utils.misc import qd_to_numpy

is_hibernated = qd_to_numpy(scene.rigid_solver.links_state.is_hibernated, transpose=True)
n_awake = is_hibernated.size - is_hibernated.sum()
```


## See also

- {doc}`constraints`: how contacts, joint limits, and equality constraints are solved for the resulting motion.
- {doc}`/user_guide/sensing/contact`: contact and tactile sensors for per-step readings.
- [`examples/rigid/hibernation.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/hibernation.py): drops a grid of objects and plots the step rate against the awake-body count as they settle.
- {doc}`/user_guide/developers/profiling`: measuring simulation throughput.
