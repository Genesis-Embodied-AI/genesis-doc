# Collision detection

The second layer of a step finds which rigid bodies touch, generates a contact manifold for each touching pair, and hands those contacts to the constraint solver. This page covers how detection works, how to read the resulting contacts back into Python, and the support field the convex algorithms rest on. For turning those contacts into accelerations, see {doc}`constraints`.

## How contacts are detected

Detection runs in two phases each step, from a cheap approximate cull to an exact contact manifold.

**Broad phase.** Each geometry gets a world-space axis-aligned bounding box (AABB), recomputed every step because rigid bodies move. A Sweep-and-Prune pass then reports only the geometry pairs whose boxes overlap, turning an all-pairs comparison into a near-linear one. The same pass drops pairs that cannot physically collide:

- **Adjacency:** two geometries on the same link, or on directly connected links.
- **Collision masks:** pairs excluded by their `contype` / `conaffinity` bitmasks.
- **Static pairs:** two geometries both fixed relative to the world.
- **Hibernation:** contacts between sleeping bodies, unless one side is awake.

**Narrow phase.** The solver resolves each surviving pair to an exact contact manifold: a contact normal, a penetration depth, and one or more contact points. The algorithm depends on the geometry pair:

| Geometry pair | Path |
|---|---|
| General convex–convex, including plane–convex | Minkowski Portal Refinement (MPR) by default, with GJK and EPA refining the contacts MPR cannot resolve reliably. GJK with EPA throughout when `use_gjk_collision=True`. |
| Plane–box and box–box | Analytic special case, for stability when a box lies flush on a plane. |
| Any geometry against height-field terrain | Terrain routine that can emit several contact points per supporting cell. |
| Non-convex meshes | Signed-distance-field sampling: vertices first (vertex–face), then edges (edge–edge), keeping the deepest penetration. |

MPR and GJK both operate through a *support function* ("which vertex lies farthest along a given direction?") so they run branch-free on the GPU without face-adjacency caches. GJK additionally reports a separation distance when the geometries are apart and is the differentiable path. It is the more stable of the two and much the slower, so we default to MPR and turn GJK on automatically when the scene requires gradients. With MPR, GJK only refines a contact when MPR did not converge on it, or when the overlap of the two geoms along their frame axes shows the portal MPR found is not the minimal one. Both accelerate support queries with a precomputed support field, described [below](#support-functions). To capture flush faces rather than a single point, Genesis perturbs the pose slightly around the first contact normal and gathers the extra contacts that result.

The `max_collision_pairs` option on {doc}`RigidOptions </api_reference/engine/solvers/rigid_solver>` bounds how many candidate pairs the broad phase may emit. Exceeding it at runtime halts the simulation, so raise it for scenes with dense contact.

## Reading contacts

To read contacts and contact forces from a script, see {doc}`Contact and force sensors </user_guide/sensing/contact>`.

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

Because neither algorithm inspects faces or edges, a shape only needs to answer support queries to participate in collision detection.

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

Only convex meshes use the field. It precomputes the answer for a dense set of directions once, then answers any query by table lookup. The collider builds it when the scene is built: one table for every geometry except height-field terrain, shared by the geometries of the same trimesh.

### Precomputation

Genesis covers the unit sphere of directions with two spherical charts, the poles of the second a quarter turn away from those of the first. Each chart answers for the band of directions 45 to 135 degrees off its own poles, and stores only the cells of that band. The resolution is `support_res = 120`, giving $2 \times 120 \times 60 = 14{,}400$ cells per table. Cell $(i, j)$ of a chart maps to angles

$$
\theta = \frac{i}{\text{res}}\,2\pi - \pi \in [-\pi, \pi), \qquad
\phi = \frac{j}{\text{res}}\,\pi \in [\pi/4, 3\pi/4),
$$

and to the direction $d = (\sin\phi\cos\theta,\; \sin\phi\sin\theta,\; \cos\phi)$ in the chart's own coordinates, with angles in radians.

For each table, Genesis lists every vertex that can support a direction of the cell: the supports of its four corners, the vertices of the hull faces whose normal falls inside the cell, and the two vertices of every hull edge whose arc crosses it. Each candidate is stored with its position in the mesh's local frame and its index. The first two candidates of a cell go in a record at the index of the cell, and the others in a list apart. The results for all tables are packed into flat arrays, so a single query needs no host round-trip.

### Query

A query rotates the world-space direction into the mesh's local frame, looks up the precomputed candidates, and transforms the winner back to world space. The lookup hands the direction to the chart whose polar axis it is least aligned with, which keeps it at least 45 degrees off that chart's poles, inverts the chart's mapping (`theta = atan2(d_y, d_x)`, `phi = acos(d_z)`) to find the cell the direction falls in, and keeps the candidate of that cell with the largest dot product. Most cells list at most two candidates, so a query reads a few vertices instead of scanning all of them.

Since a cell lists every vertex that can support its directions, the field can also report how many distinct vertices tie for the maximum. GJK uses that count to detect directions where the support point is ambiguous and perturb the query, which keeps the algorithm numerically stable on flat faces and shared edges.

### Data layout

The field lives in a Quadrants-resident struct of flat arrays, so collision kernels read it without pointer chasing. A prefix-sum offset indexes into the concatenated per-table blocks.

| Field | Shape | Description |
|---|---|---|
| `support_v` | `(2 n_support_cells + n_extras, 3)` | Candidate vertex positions, in each geometry's local frame: the record of every cell, then the extra candidates of all cells. |
| `support_vid` | `(2 n_support_cells + n_extras,)` | Corresponding vertex index in the original mesh. |
| `support_list_start` | `(n_support_cells + 1,)` | Start of the extra candidates of each cell. |
| `support_cell_start` | `(n_geoms,)` | Offset of each geometry's table into the flattened arrays. Geometries sharing a trimesh share a table. |

Each distinct trimesh contributes $14{,}400$ cells. A cell's record holds two candidates (three floats plus one integer each), roughly 0.5 MB per table at single precision, plus the extra candidates of the cells crossed by several hull features.

### Trade-offs

- **Short lookups:** a query scans the candidates of a single cell rather than every vertex.
- **Uniform representation:** every convex mesh reduces to the same struct-of-arrays layout, with no per-shape bounding volume or hierarchy to build or traverse.
- **Exact:** each cell lists every vertex whose normal cone meets it, so the lookup returns the true extreme point, up to the angle error of the binning in single precision.
- **Fixed preprocessing cost:** the field is built once per distinct trimesh at scene build time (instances of an asset share one table, and terrain gets none), so both build time and memory grow with the number of distinct meshes in the scene.

:::{note}
When MuJoCo compatibility is enabled, a mesh query falls back to an exhaustive vertex scan for bit-level agreement with MuJoCo.
:::

## Contact islands and hibernation

The solver partitions the scene into **contact islands**: the connected components of a coupling graph whose nodes are the kinematic trees that carry dofs, joined by contacts and by equality constraints. An articulated body stays one island; an entity holding several free bodies splits into one island per body. Each island is an exactly decoupled block of the constraint solve, so the solver factors and solves every island on its own instead of assembling one system for the whole scene. A scene made of a single coupled tree forms one island.

**Hibernation** extends that partition in time. Each substep, the solver compares every awake link's maximum degree-of-freedom (dof) speed against `hibernation_thresh_vel`. It weights each dof velocity by its `dof_length`, which is 1 for a translational dof and the swept radius for a rotational one, so a single linear tolerance covers both and the rotational jitter of a small body does not keep it awake. A link that stays under the tolerance for 10 consecutive substeps is ready to sleep, and an island hibernates once all of its links are ready, at which point the solver zeroes their dof velocities. Three things wake an island again: a new contact against one of its bodies (resolved before the solve, so the body responds the same step), actuation of one of its links, and a coupling force arriving from another solver.

A sleeping island is skipped by the solve and by the broad phase. In a scene with many settled bodies, per-step cost then follows the number of *awake* bodies rather than the total.

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        use_hibernation=True,
    ),
)
```

There are no `hibernate()` or `wake()` calls: two options drive the whole mechanism. `use_hibernation` defaults to `False`, and `hibernation_thresh_vel` is the speed below which a link may sleep, in m/s, defaulting to `1e-4` under MuJoCo compatibility and `2e-3` otherwise.

:::{note}
The gain is largest on the CPU backend, where skipping sleeping islands raises the serial step rate directly. Hibernation stays off in a differentiable scene, because the adjoint pass needs every body in the iteration trace.
:::

Read which links are asleep from the solver state:

```python
from genesis.utils.misc import qd_to_numpy

is_hibernated = qd_to_numpy(scene.rigid_solver.dyn_state.links.is_hibernated, transpose=True)
n_awake = is_hibernated.size - is_hibernated.sum()
```


## See also

- {doc}`constraints`: how contacts, joint limits, and equality constraints are solved for the resulting motion.
- {doc}`/user_guide/sensing/contact`: contact and tactile sensors for per-step readings.
- [`examples/rigid/hibernation.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/hibernation.py): drops a grid of objects and plots the step rate against the awake-body count as they settle.
- {doc}`/user_guide/performance/profiling`: measuring simulation throughput.
