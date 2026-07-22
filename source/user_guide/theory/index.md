# Theory and Modelling

This section explains how the engine works underneath the API. Where the rest of the guide is task-oriented, these pages are reference material for the physics and algorithms: what happens inside a `scene.step()`, how contacts are found and resolved, how one scene runs several solvers (rigid, FEM, MPM, SPH, PBD) at once and keeps them consistent, and the material models behind deformation. Read them when a result surprises you, when you are tuning a hard contact or coupling problem, or when you simply want to understand the machinery.

```{toctree}
:hidden:
:maxdepth: 2

rigid_collision/index
solvers_and_coupling
couplers/index
nonrigid_models
differentiable_simulation
support_field
hibernation
```
