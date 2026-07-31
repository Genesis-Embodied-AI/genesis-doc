# Rigid solver

The rigid solver advances articulated rigid bodies: robots, mechanisms, and rigid objects. Every `scene.step()` runs it in three layers.

1. **{doc}`forward_dynamics`.** Place the links from the joint positions, build the mass matrix, and solve for the acceleration under the forces that do not depend on contact.
2. **{doc}`collision_detection`.** Cull the geometry pairs that cannot touch, then compute exact contacts for those that remain. That page also covers the support field behind the convex algorithms, and the contact islands hibernation builds on.
3. **{doc}`constraints`.** Turn those contacts, joint limits, and equality constraints into forces, and correct the acceleration.

The layers are configured through {py:class}`gs.options.RigidOptions <genesis.options.solvers.RigidOptions>`.

A {doc}`coupler </user_guide/theory/coupling/index>` handles soft-body and particle contact against rigid geometry.

```{toctree}
:hidden:
:maxdepth: 1

forward_dynamics
collision_detection
constraints
```
