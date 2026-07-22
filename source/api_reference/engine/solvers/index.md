# Solvers

A solver is the physics engine for one class of material. Each solver owns the entities built from its materials, advances their state every substep, and exposes the state back to the scene. A scene can run several solvers at once, so a single simulation can mix rigid robots, deformable solids, cloth, fluids, and smoke. For how solvers exchange forces at their interfaces, see {doc}`/user_guide/theory/solvers_and_coupling`.

You rarely construct a solver directly. You add an entity with a material, and the scene routes it to the matching solver; you configure each solver through its options object. For how to combine solvers in one scene and choose between them, see {doc}`/user_guide/physics/beyond_rigid_bodies` and {doc}`/user_guide/theory/solvers_and_coupling`.

:::{note}
`ToolSolver` is a temporary solver that provides one-way differentiable coupling from a rigid tool to soft bodies. It will be removed once the `RigidSolver` supports differentiability directly.
:::

```{toctree}
:titlesonly:

rigid_solver
mpm_solver
fem_solver
pbd_solver
sph_solver
sf_solver
tool_solver
kinematic_solver
```

## See also

- {doc}`/user_guide/theory/solvers_and_coupling`: how solvers are combined and coupled.
- {doc}`/api_reference/engine/couplers/index`: the couplers that exchange forces between solvers.
