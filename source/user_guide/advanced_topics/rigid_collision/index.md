# Rigid collision

Every simulation step, Genesis World finds which rigid bodies touch and computes the forces that keep them from interpenetrating. This section explains that process at a conceptual level so you can extend or debug it. It covers rigid–rigid interactions only; soft-body and particle contacts are handled by separate couplers.

## The collision pipeline at a glance

Genesis World resolves rigid contacts in two conceptual halves: first *detection* (which bodies are in contact, and where), then *resolution* (what forces cancel the contact). Detection itself runs in stages, from a cheap approximate cull to an exact contact manifold:

- **Broad phase:** rejects pairs of geometries that cannot possibly touch. Each geometry gets a world-space axis-aligned bounding box (AABB), and a Sweep-and-Prune pass reports only the pairs whose boxes overlap. This turns an all-pairs comparison into a near-linear one, and it filters out pairs that are physically irrelevant, such as adjacent links or bodies on disjoint collision masks.
- **Narrow phase:** takes each surviving pair and computes an exact contact manifold: the contact normal, penetration depth, and contact points. Different geometry combinations take different algorithmic paths: general convex pairs use MPR (or GJK, when enabled), meshes fall back to signed-distance fields, and box and terrain cases use specialized routines.
- **Contacts:** the manifolds land in a struct-of-arrays contact buffer that the constraint solver reads. Each contact carries its geometries, normal, penetration, and the effective friction coefficient.
- **Constraint solve:** the contacts, together with joint limits and equality constraints, form a single system solved for the generalized accelerations that satisfy every constraint at once. Genesis World uses a soft, MuJoCo-style quadratic formulation solved by either a projected conjugate-gradient or a Newton–Cholesky method.

Convex detection leans on a precomputed acceleration structure that answers "which vertex lies farthest along a given direction?" in constant time. See {doc}`/user_guide/advanced_topics/support_field` for how that field is built and used.

## In this section

- **{doc}`collision_contacts_forces`:** detection: broad-phase pruning and the narrow-phase algorithms (Sweep-and-Prune, GJK, MPR, and the mesh, terrain, and box special cases) that generate contact manifolds.
- **{doc}`rigid_constraint_model`:** resolution: the constraint formulation, the contact and friction model, joint limits, equality constraints, and the numerical solvers.

```{toctree}
:hidden:
:maxdepth: 1

collision_contacts_forces
rigid_constraint_model
```
