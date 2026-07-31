# Theory and Modelling

This section explains how the engine works underneath the API. Where the rest of the guide is task-oriented, these pages are reference material for the physics and algorithms. Read them when a result surprises you, when you are tuning a hard contact or coupling problem, or when you simply want to understand the machinery.

## What happens in a physics step

A rigid-body engine is three layers, and every `scene.step()` runs them in order. Which layer produced a surprising result is most of the diagnosis, since each fails differently.

1. **Forward dynamics.** Place the links, build the mass matrix, sum the forces independent of contact, solve for the acceleration. Fails as sag under gravity, joints gaining energy, or instability as `dt` grows.
2. **Collision detection.** Cull the pairs that cannot meet, then compute exact contacts for the rest. Fails as a contact that never appears or a normal pointing somewhere implausible, which is usually the collision geometry rather than the solver.
3. **Constraint solving.** Turn contacts, joint limits, and equality constraints into forces, correcting the acceleration. Fails as interpenetration, jitter at rest, or a stack that will not settle.

The step then integrates the corrected acceleration and refreshes the link poses. With `substeps > 1`, all three run once per substep.

Above them sits everything that is not the rigid physics: the non-rigid solvers, the couplers that let them share a scene, differentiability, and the optimizations that skip work.

## In this section

**The three layers**

- **{doc}`forward_dynamics`:** kinematics, the composite-rigid-body mass matrix, the forces preceding contact, the integration schemes, and `dt` against `substeps`.
- **{doc}`rigid_collision/index`:** the broad and narrow phases, what a contact carries, reading contacts back, and the support field convex detection rests on.
- **{doc}`rigid_constraint_model`:** the constraint system, friction cones and contact resolutions, joint limits, equality constraints, and the numerical solvers.

**Beyond rigid bodies**

- **{doc}`nonrigid_models`:** the material models behind deformable solids, liquids, cloth, and muscles.
- **{doc}`solvers_and_coupling`:** how one scene runs several solvers at once and keeps them consistent.
- **{doc}`couplers/index`:** the three couplers, what each models at a solver interface, and how to choose.

**Across the whole engine**

- **{doc}`differentiable_simulation`:** how gradients flow through a step, and what is not differentiable.
- **{doc}`hibernation`:** letting the solver skip entities that have come to rest.

## Further reading

These pages aim at the middle: enough of the model to reason about a result or choose an option, stopping short of deriving the numerics. For the derivations, [Physics-Based Simulation](https://phys-sim-book.github.io/) (Li, Jiang, et al.) is a free online book that develops this material formally and in far more mathematical depth.

```{toctree}
:hidden:
:maxdepth: 2

forward_dynamics
rigid_collision/index
rigid_constraint_model
nonrigid_models
solvers_and_coupling
couplers/index
differentiable_simulation
hibernation
```
