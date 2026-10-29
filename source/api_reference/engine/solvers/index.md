# Solvers

A solver is the physics engine for one family of entities. Each solver owns the entities built from its entity options, advances their state every substep, and exposes the state back to the scene. A scene can run several solvers at once, so a single simulation can mix rigid robots, deformable solids, cloth, fluids, and smoke. For how solvers exchange forces at their interfaces, see {doc}`/user_guide/physics/coupling/index`.

You rarely construct a solver directly. Add an entity with entity options and the scene routes it to the solver their class names; configure that solver through its options object. For how to combine solvers in one scene and choose between them, see {doc}`/user_guide/physics/beyond_rigid_bodies` and {doc}`/user_guide/physics/coupling/index`.

```{toctree}
:titlesonly:

rigid_solver
mpm_solver
fem_solver
pbd_solver
sph_solver
sf_solver
kinematic_solver
```

## See also

- {doc}`/user_guide/physics/coupling/index`: how solvers are combined and coupled.
- {doc}`/api_reference/engine/couplers/index`: the couplers that exchange forces between solvers.
