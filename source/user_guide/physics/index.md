# Physical Entities

A Genesis World scene is not limited to rigid robots: the same {py:class}`Scene <genesis.engine.scene.Scene>` can hold water, sand, cloth, soft muscle-driven bodies, quadrotors, and terrain, each simulated by the solver suited to it and each added through the same `scene.add_entity(...)` call. Rigid bodies are the default and the foundation, so start there; the remaining pages cover the non-rigid and specialized families. How different solvers interact where their entities touch is covered separately under {doc}`Theory and Modelling </user_guide/theory/index>`.

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
