# The support field

Genesis World detects collisions between convex shapes with algorithms that never touch a shape's full geometry directly. Instead, they ask one question repeatedly: *given a direction, which point of the shape lies farthest that way?* The answer is called a **support point**, the function that returns it is a **support function**, and the **support field** is the acceleration structure that answers this question in constant time for arbitrary convex meshes.

This page explains what support functions are, why the collision pipeline is built on them, and how Genesis precomputes a support field so that mesh queries stay cheap. For where these queries sit in the broader pipeline, see {doc}`rigid_collision/index`.

## The support function

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

Because neither algorithm inspects faces or edges, a shape only needs to answer support queries to participate in collision detection. That is why the support function, not the mesh, is the real interface.

## Support functions in Genesis

Genesis dispatches each support query by geometry type. The dispatch lives in `support_driver` in `genesis/engine/solvers/rigid/collider/gjk_support.py`, which routes to a dedicated device function per shape:

| Geometry | Support function | How it computes the extreme point |
|---|---|---|
| Sphere | `_func_support_sphere` | Center offset by the radius along $d$. |
| Ellipsoid | `_func_support_ellipsoid` | Closed form from the direction in the local frame. |
| Capsule | `_func_support_capsule` | Endpoint selected by the sign of $d$ along the axis, offset by the radius. |
| Cylinder | `_func_support_cylinder` | Rim point of the cap selected along the axis. |
| Box | `_func_support_box` | Corner chosen by the sign of $d$ in each local axis. |
| Terrain | `_func_support_prism` | Extreme vertex of the active prism cell. |
| Convex mesh | `_func_support_world` | Table lookup into the precomputed support field. |

Primitives have analytical support functions: the extreme point follows directly from a formula, so no search is needed. A general convex mesh has no such formula. The naive answer is to project every vertex onto $d$ and take the maximum, which costs $O(N)$ per query for a mesh of $N$ vertices, and both GJK and MPR issue many queries per contact pair, per step. The support field exists to remove that cost.

## The support field for convex meshes

The support field, implemented by the `SupportField` class in `genesis/engine/solvers/rigid/collider/support_field.py`, precomputes the answer for a dense set of directions once, then answers any query by table lookup. The collider builds and activates one instance when the scene is built.

### Precomputation

The unit sphere of directions is sampled on a regular latitude–longitude grid of `support_res × support_res` cells. The default resolution is `support_res = 180`, giving $180 \times 180 = 32{,}400$ sample directions. Cell $(i, j)$ maps to angles

$$
\theta = \frac{i}{\text{res}}\,2\pi - \pi \in [-\pi, \pi), \qquad
\phi = \frac{j}{\text{res}}\,\pi \in [0, \pi),
$$

and to the direction $d = (\sin\phi\cos\theta,\; \sin\phi\sin\theta,\; \cos\phi)$, with angles in radians.

For each geometry, Genesis projects all of its vertices onto every sample direction and records the winning vertex: its position in the mesh's local frame and its index. The results for all geometries are packed into flat arrays, so a single query needs no host round-trip.

### Query

At query time, `_func_support_world` rotates the world-space direction into the mesh's local frame, looks up the precomputed vertex, and transforms it back to world space:

```python
d_mesh = gu.qd_transform_by_quat(d, gu.qd_inv_quat(quat))
v_, vid = _func_support_mesh(support_field_info, d_mesh, i_g)
v = gu.qd_transform_by_trans_quat(v_, pos, quat)
```

The lookup itself inverts the grid mapping (`theta = atan2(d_y, d_x)`, `phi = acos(d_z)`) to find the continuous cell coordinates, then evaluates the four cells bracketing them (`floor` and `ceil` of each coordinate) and keeps the vertex with the largest dot product. This is a fixed, four-cell search regardless of mesh size, so the query is $O(1)$ in the vertex count.

The four-cell neighborhood also lets the field report how many distinct vertices tie for the maximum (`_func_count_supports_world`). GJK uses that count to detect directions where the support point is ambiguous and perturb the query, which keeps the algorithm numerically stable on flat faces and shared edges.

## Data layout

The field is stored as a struct of flat arrays in a Quadrants-resident structure so collision kernels read it without pointer chasing. Per-geometry blocks are concatenated and indexed through a prefix-sum offset.

| Field | Shape | Description |
|---|---|---|
| `support_v` | `(n_support_cells, 3)` | Winning vertex positions, in each geometry's local frame. |
| `support_vid` | `(n_support_cells,)` | Corresponding vertex index in the original mesh. |
| `support_cell_start` | `(n_geoms,)` | Offset of each geometry's block into the flattened arrays. |

At the default resolution, each convex mesh contributes $32{,}400$ cells. At single precision (three floats plus one integer per cell) that is roughly 0.5 MB per mesh, independent of the mesh's vertex count.

## Trade-offs

- **Constant-time lookups:** a query is a fixed four-cell search rather than a scan over vertices, which also means fewer diverging branches on the GPU.
- **Uniform representation:** every convex mesh reduces to the same struct-of-arrays layout, with no per-shape bounding volume or hierarchy to build or traverse.
- **Approximate, not exact:** the grid has a fixed angular resolution, so a query direction snaps to the nearest sampled cells. A feature narrower than one angular cell may return a neighboring vertex rather than the true extreme point.
- **Fixed preprocessing cost:** the field is built for every geometry at scene build time and stored at full resolution, so both build time and memory grow with the number of geometries in the scene.

:::{note}
Only convex meshes use the support field. Primitives use their analytical support functions above, and when MuJoCo compatibility is enabled a mesh query falls back to an exhaustive vertex scan (`support_mesh`) for bit-level agreement with MuJoCo.
:::

## See also

- {doc}`rigid_collision/index`: where GJK and MPR fit in the rigid collision pipeline, from broad-phase pruning to contact generation.
