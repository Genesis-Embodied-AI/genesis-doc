# Rigid collision detection

The second of the engine's {doc}`three layers </user_guide/theory/index>`: once {doc}`forward dynamics </user_guide/theory/forward_dynamics>` has moved the bodies, detection consumes their geom poses and produces contacts. It computes no forces; that is the {doc}`constraint model </user_guide/theory/rigid_constraint_model>`.

This section covers rigid-rigid interactions; soft-body and particle contacts are handled by the {doc}`couplers </user_guide/theory/couplers/index>`.

## The detection pipeline at a glance

Detection runs in stages, from a cheap approximate cull to an exact contact manifold:

- **Broad phase:** rejects pairs of geometries that cannot possibly touch. Each geometry gets a world-space axis-aligned bounding box (AABB), and a Sweep-and-Prune pass reports only the pairs whose boxes overlap. This turns an all-pairs comparison into a near-linear one, and it filters out pairs that are physically irrelevant, such as adjacent links or bodies on disjoint collision masks.
- **Narrow phase:** takes each surviving pair and computes an exact contact manifold: the contact normal, penetration depth, and contact points. Different geometry combinations take different algorithmic paths: general convex pairs use MPR (or GJK, when enabled), meshes fall back to signed-distance fields, and box and terrain cases use specialized routines.
- **Contacts:** the manifolds land in a struct-of-arrays contact buffer that the constraint solver reads. Each contact carries its geometries, normal, penetration, and the effective friction coefficient.

This layer reports only what the geometry says, so the collision geometry determines its output: an undecomposed concave mesh, or a visual mesh pressed into service as a collider, yields missing or implausible contacts that no solver tuning fixes.

## In this section

- **{doc}`collision_contacts_forces`:** the broad and narrow phases in detail, what each contact carries, and how to read contacts back from a stepped scene.
- **{doc}`support_field`:** the precomputed structure that answers "which vertex lies farthest along this direction?" in constant time, which is what makes convex narrow-phase queries cheap.

```{toctree}
:hidden:
:maxdepth: 1

collision_contacts_forces
support_field
```
