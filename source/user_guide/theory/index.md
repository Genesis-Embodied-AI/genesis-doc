# Theory and Modelling

This section explains how the engine works underneath the API. Where the rest of the guide is task-oriented, "how do I add a sensor, control a robot, load a mesh", these pages are reference material for the physics and the algorithms: what happens inside a `scene.step()`, how contacts are found and resolved, how different solvers share one scene, and the material models that govern deformation. Read them when a result surprises you, when you are tuning a hard contact or coupling problem, or when you simply want to understand the machinery.

The unifying fact is that a single `Scene` can run several physics solvers at once, rigid, FEM, MPM, SPH, PBD, and still behave as one consistent world. Most of this section is about how that is made to work: the collision and constraint pipeline for rigid bodies, the couplers that reconcile solvers where their entities meet, the constitutive models behind non-rigid materials, and the shared primitives (the support field) and optimizations (hibernation) underneath.

- {doc}`rigid_collision/index` details the rigid pipeline that runs every step: detecting which bodies touch, building contact manifolds, and solving the constraint forces that keep them from interpenetrating.
- {doc}`solvers_and_coupling` is the overview of multi-physics: which solvers exist, what each simulates, and how a scene runs them together.
- {doc}`couplers/index` covers the components that resolve interaction between solvers, including the SAP and IPC contact models.
- {doc}`nonrigid_models` explains the constitutive models, the stress-strain relationships, behind deformable and fluid materials.
- {doc}`support_field` describes the support-function abstraction the convex collision algorithms query instead of touching full geometry.
- {doc}`hibernation` explains how the solver puts settled rigid bodies to sleep to skip work, and what wakes them.

```{toctree}
:hidden:
:maxdepth: 2

rigid_collision/index
solvers_and_coupling
couplers/index
nonrigid_models
support_field
hibernation
```
