# Theory and Modelling

This section explains how the engine works underneath the API. Where the rest of the guide is task-oriented, these pages are reference material for the physics and algorithms. Read them when a result surprises you, when you are tuning a hard contact or coupling problem, or to understand the machinery.

A `scene.step()` advances every active solver by `dt`, or by `dt / substeps` per substep, and the coupler reconciles them in between. Which solver holds an entity follows from its material.

## In this section

- **{doc}`rigid_solver/index`:** the three layers of a rigid step (forward dynamics, collision detection, and the constraint solve), plus hibernation.
- **{doc}`soft_solvers`:** the five continuum and particle solvers, and the constitutive models they integrate.
- **{doc}`coupling/index`:** how solvers exchange forces where their materials meet, and which coupler to use.
- **{doc}`differentiable_simulation`:** how gradients flow through a step.

## Further reading

These pages describe the models Genesis World implements and the options that select them; they do not derive them. For the derivations, [Physics-Based Simulation](https://phys-sim-book.github.io/) (Li, Jiang, et al.) is a free online book on the theory and algorithms of physics-based simulation.

```{toctree}
:hidden:
:maxdepth: 2

rigid_solver/index
soft_solvers
coupling/index
differentiable_simulation
```
