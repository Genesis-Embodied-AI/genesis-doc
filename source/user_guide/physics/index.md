# Physical Entities

A Genesis World scene is not limited to rigid robots. The same `Scene` can hold water, sand, cloth, soft muscle-driven bodies, quadrotors, and terrain, each simulated by the solver suited to it, and each added through the same `scene.add_entity(...)` call you already know. This section is the tour of those entity families: what each one is, when to reach for it, and the material and morph options that define it.

Rigid bodies are the default and the foundation, so start there; the remaining pages cover the non-rigid and specialized families that build on the same API. How these different solvers interact when entities of different types touch, the coupling that makes a multi-physics scene consistent, is a separate topic covered under {doc}`Theory and Modelling </user_guide/theory/index>`.

- {doc}`rigid_bodies` is the default entity type and the overview for the rest: a solid that does not deform, covering most of robotics, arms, grippers, mobile bases, and the props they interact with.
- {doc}`beyond_rigid_bodies` introduces the deformable and fluid families, cloth, liquids, granular media, and elastic solids, and the solvers behind them.
- {doc}`soft_robots` covers deformable bodies driven by embedded **muscle fibers** rather than joint motors.
- {doc}`hybrid_entity` couples a rigid skeleton to a soft skin so the two simulate as one body.
- {doc}`drone_entity` is the quadrotor entity, actuated by four propeller speeds instead of joint commands.
- {doc}`terrain` builds a static rigid ground from a height field, the standard ground for locomotion work.
- {doc}`emitters` stream particles into a particle solver as the simulation runs, for continuous sources like a hose or a nozzle.
- {doc}`force_fields` apply a spatially varying acceleration to an entity's particles every substep, for wind, vortices, and other body forces.

```{toctree}
:hidden:
:maxdepth: 1

rigid_bodies
beyond_rigid_bodies
soft_robots
hybrid_entity
drone_entity
terrain
emitters
force_fields
```
