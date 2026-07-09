# Concepts and Configuration

The {doc}`Getting Started </user_guide/getting_started/index>` tutorials show what a Genesis World program looks like; this section explains why it looks that way and how to configure every part of it. Its throughline is the two-phase model at the heart of the API: you first *describe* a scene by adding entities and options, then *build* it once and *step* it. Almost every configuration choice is made in the describe phase and frozen at build time, so knowing what belongs where is what keeps a program correct.

Read this section when you want to move past copying a tutorial and reason about the object model, choose backends and precision deliberately, set options in a principled way, or save and restore simulation state. The pages progress from the concepts every program relies on to the specific knobs you turn.

- {doc}`concepts` is the object and computation model: how a scene contains entities and a simulator, how the describe-then-build phases work, and the local-versus-global indexing scheme that lets one entity address its own slice of a solver's data.
- {doc}`initialization` covers `gs.init()`: selecting the compute backend, fixing numeric precision, and seeding randomness, all decisions made once before any scene exists.
- {doc}`config_system` explains the typed **options objects** under `gs.options.*` that configure the scene, the solvers, and each entity, and how they compose.
- {doc}`conventions` is the reference for the coordinate system, rotation representations, physical units, tensor shapes, and data types the whole API shares.
- {doc}`checkpoints` shows how to snapshot the dynamic state of a scene and restore it, for resetting, branching, or resuming a simulation.

```{toctree}
:hidden:
:maxdepth: 1

concepts
initialization
config_system
conventions
checkpoints
```
