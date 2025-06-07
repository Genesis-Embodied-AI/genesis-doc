# 💥 Collision, Contacts & Forces

Genesis provides a highly-efficient, feature-rich collision detection and contact generation pipeline for rigid bodies.  The Python implementation lives in `genesis/engine/solvers/rigid/collider_decomp.py`.  This page gives a *conceptual* overview of the algorithmic building blocks so that you can understand, extend or debug the code.

> **Scope.**  The focus is on rigid–rigid interactions.  Soft-body / particle collisions rely on different solvers and are documented elsewhere.

---

## Pipeline Overview

``{figure} ../../_static/images/collision_pipeline.png
:alt: Collision pipeline
:width: 750px
``

The whole procedure can be seen as three successive stages:

1. **AABB Update** – update world–space Axis-Aligned Bounding Boxes for every geometry.
2. **Broad Phase (Sweep-and-Prune)** – quickly reject obviously non-intersecting pairs and output *possible* collision pairs.
3. **Narrow Phase** – robustly compute the actual contact manifold (normal, penetration depth, position, etc.) for every surviving pair.

`Collider` orchestrates all three stages through the public `detection()` method:

```python
collider.detection()  # updates AABBs → SAP broad phase → narrow phase(s)
```

Each stage is described in the following sections.

---

## 1&nbsp;· AABB Update

The helper kernel `_func_update_aabbs()` delegates the work to `RigidSolver._func_update_geom_aabbs()`.  It computes a *tight* world-space AABB per geometry and stores the result in `geoms_state[..].aabb_min / aabb_max`.

Why do we do this every frame?

* Rigid bodies move ⇒ their bounding boxes change.
* AABB overlap checks are the cornerstone of the broad phase.

!!! tip "Numerical stability"
    AABBs are expanded by a small margin internally to keep objects from tunnelling due to floating-point errors.

---

## 2&nbsp;· Broad Phase – Sweep & Prune

The broad phase is implemented in `_func_broad_phase()`.  It is an *N·log N* insertion-sort variant of the classical Sweep-and-Prune (a.k.a. Sort-and-Sweep):

1.  Project every AABB onto a single axis (currently X) and insert its *min* and *max* endpoints into a sortable buffer.
2.  **Warm-start** – the endpoints are already almost sorted from the previous frame ⇒ insertion sort is almost linear.
3.  Sweep through the sorted buffer maintaining an *active set* of intervals that overlap the current endpoint.
4.  Whenever `min_a` crosses inside `max_b` we have a *potential* pair `(geom_a, geom_b)`.

Extra filtering steps remove pairs that are physically impossible or explicitly disabled:

* Same link / adjacent link filtering.
* `contype`/`conaffinity` bitmasks.
* Pairs of links that are both fixed w.r.t. the world.
* *Hibernation* support – sleeping bodies are ignored unless colliding with awake ones.

The surviving pairs are stored in `broad_collision_pairs` and `n_broad_pairs`.

---

## 3&nbsp;· Narrow Phase – Contact Manifold Generation

The narrow phase is split into three specialised kernels:

| Kernel | When it runs | Purpose |
|--------|--------------|---------|
| `_func_narrow_phase_terrain` | at least one geometry is a *height-field terrain* | generate multiple contact points per supporting cell.
| `_func_narrow_phase` | convex–convex & plane–anything | Default path using **MPR** (Minkowski Portal Refinement) with fall-back to signed-distance-field queries.
| `_func_narrow_phase_nonconvex_nonterrain` | at least one geometry is **non-convex** | Handles mesh ↔ convex or mesh ↔ mesh collisions via SDF vertex/edge sampling.

### 3.1&nbsp; Convex–Convex via MPR

MPR is favoured because it is:

* Robust for deep penetration.
* Runs entirely on the GPU thanks to branch-free support-mapping primitives.
* Requires only a *support function* per shape – no face adjacency or feature cache.

Genesis accelerates support queries with a **pre-computed Support Field** (see {doc}`Support Field <support_field>`).

Multi-contact generation is enabled by *small pose perturbations* around the first contact normal.  At most five contacts (`_n_contacts_per_pair = 5`) are stored per pair.

### 3.2&nbsp; Non-convex Objects

For triangle meshes or decomposed convex clusters the pipeline uses **signed-distance fields** (SDF) pre-baked offline.  The algorithm samples

* vertices (vertex–face contact), then
* edges (edge–edge contact)

and keeps the deepest penetration.  The costly edge pass is skipped if a vertex contact is already found.

### 3.3&nbsp; Plane ↔ Box Special-Case

Mujoco's analytical plane–box and box–box routine is ported for extra stability and to avoid degeneracies when a box lies flush on a plane.

---

## Contact Data Layout

Successful contacts are pushed into the *struct-of-arrays* field `contact_data`:

| Field | Meaning |
|-------|---------|
| `geom_a`, `geom_b` | geometry indices |
| `penetration` | positive depth (≤ 0 means separated) |
| `normal` | world-space unit vector pointing **from B to A** |
| `pos` | mid-point of inter-penetration |
| `friction` | effective Coulomb coefficient (max of the two) |
| `sol_params` | solver tuning constants |

`n_contacts` is incremented atomically so that GPU kernels may append in parallel.

---

## Warm-Start & Caching

To improve temporal coherence we cache, for every geometry pair, the ID of the previously deepest vertex and the last known separating normal.  The cache is consulted to *seed* the MPR search direction and is cleared when the pair separates in the broad phase.

---

## Hibernation

When the *sleeping bodies* feature is enabled, contacts belonging exclusively to hibernated bodies are preserved but not re-evaluated every frame (`n_contacts_hibernated`).  This drastically reduces GPU work for scenes with large static backgrounds.

---

## Tuning Parameters

| Option | Default | Effect |
|--------|---------|--------|
| `RigidSolver._max_collision_pairs` | 4096 | upper bound on broad-phase pairs (per environment) |
| `Collider._mc_perturbation` | `1e-2` rad | perturbation angle for multi-contact search |
| `Collider._mc_tolerance`    | `1e-2` m   | duplicate-contact rejection radius |
| `Collider._mpr_to_sdf_overlap_ratio` | `0.5` | threshold to switch from MPR to SDF when one shape encloses the other |

---

## Further Reading

* {doc}`Support Field <support_field>` – offline acceleration structure for support-mapping shapes.
* [Minkowski Portal Refinement – Gino van den Bergen 2005](https://caseymuratori.com/blog_0003) (original paper).
* *Real-Time Collision Detection* – Christer Ericson, 2004.
