# 🚀 Support Field

Collision detection for convex shapes in Genesis relies heavily on *support functions*.  Every iteration of the Minkowski Portal Refinement (MPR) algorithm asks questions of the form:

> _"Given a direction **d**, which vertex of the shape has the maximum dot-product **v·d**?"_

A naïve implementation has to iterate over all vertices every time – wasteful for models containing thousands of points.  To avoid this, Genesis pre-computes a **Support Field** for every convex geometry during scene initialisation.  The implementation lives in `genesis/engine/solvers/rigid/support_field_decomp.py`.

---

## How It Works

1. **Uniform Direction Grid**  –  The sphere is discretised into `support_res × support_res` directions using longitude/latitude (`θ`, `ϕ`).  By default `support_res = 180`, giving ≈32 k sample directions.
2. **Offline Projection**      –  For each direction we project *all* vertices and remember the index with the largest dot-product.  The resulting arrays are:
   * `support_v ∈ ℝ^{N_dir×3}` – the actual vertex positions in *object space*.
   * `support_vid ∈ ℕ^{N_dir}`   – original vertex indices (useful to warm-start SDF queries).
   * `support_cell_start[i_g]`   – prefix-sum offset into the flattened arrays per geometry.
3. **Quadrants Fields** – The arrays are copied into GPU-resident Quadrants fields so that kernels can access them without host round-trips.

```python
v_ws, idx = support_field._func_support_world(dir_ws, i_geom, i_batch)
```

The above gives you the extreme point in world-space for any query direction in **O(1)**.

---

## Data Layout

| Field | Shape | Description |
|-------|-------|-------------|
| `support_v`         | `(N_cells, 3)` | vertex positions (float32/64) |
| `support_vid`       | `(N_cells,)`   | corresponding vertex index (int32) |
| `support_cell_start`| `(n_geoms,)`   | offset into flattened arrays |

!!! info "Memory footprint"
    With the default resolution each convex shape uses ≈ 32 k × (3 × 4 + 4) = 416 kB.  For collections of small primitives this is significantly cheaper than building a BVH per shape.

---

## Advantages

* **Constant-time look-ups** during MPR ⇒ fewer diverging branches on the GPU.
* **GPU friendly** – the support field is a simple SOA array, no complex pointer chasing.
* **Works for *any* convex mesh** – no need for canonical-axes or bounding boxes.

## Limitations & Future Work

* The direction grid is isotropic but not adaptive – features smaller than the angular cell size may map to the wrong vertex.
* Preprocessing and memory consumption would be expensive if the number of geometry is large in a scene.

---

## API Summary

```python
from genesis.engine.solvers.rigid.rigid_solver_decomp import RigidSolver
solver   = RigidSolver(...)
s_field  = solver.collider._mpr._support  # internal handle

v_ws, idx = s_field._func_support_world(dir_ws, i_geom, i_env)
```

`v_ws` is the *world-space* support point while `idx` is the vertex ID in the original mesh (global index).

---

## Relation to Collision Pipeline

The Support Field is an **acceleration structure** exclusively used by the *convex–convex* narrow phase.  Other collision paths – SDF, terrain, plane–box – bypass it because they either rely on analytical support functions or distance fields.

For details on how MPR integrates this structure see {doc}`Rigid Collision Detection <rigid_collision/collision_contacts_forces>`.