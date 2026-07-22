# States

A state holds the runtime data of a simulation: positions, velocities, forces, and the solver-specific variables that evolve each step. `scene.get_state()` returns a `SimState`, an aggregate snapshot of the whole scene that holds one per-solver state for each active solver:

- **RigidSolverState:** link poses, joint positions and velocities.
- **MPMSolverState:** particle positions, velocities, deformation gradients.
- **FEMSolverState:** node positions, velocities.
- **PBDSolverState:** particle positions, velocities.
- **SPHSolverState:** particle positions, velocities, densities.

## Reading state

Read state through the entity you added, rather than through the aggregate snapshot. After `scene.build()`, call the getters directly, for example `robot.get_qpos()`, `robot.get_qvel()`, or `robot.get_link("ee").get_pos()`.

The returned tensors follow the batched-optional shape convention: the leading environment dimension is present when the scene is built with multiple environments and absent otherwise. Pass `envs_idx` to read a subset. See {doc}`/user_guide/configuration/conventions` for the full shape and dtype conventions, and {doc}`/user_guide/getting_started/hello_genesis` for a worked example.

## Saving and restoring

`scene.get_state()` returns a `SimState` snapshot of the whole scene. The scene has no `set_state`: restore a snapshot by passing it to `scene.reset(state=...)`, which resets the scene to that state and registers it as the new initial state. Called without a state, `scene.reset()` restores the initial state, and `envs_idx` restricts the reset to a subset of environments. Individual solvers and entities expose their own `set_state` for finer-grained restoration, for example `scene.sim.rigid_solver.set_state(...)`.

For usage, see {doc}`/user_guide/configuration/checkpoints`.

## Gradient tracking

When the scene is built for differentiable simulation (`requires_grad=True` on `gs.options.SimOptions`), state tensors track gradients, so a loss computed from them can be backpropagated. See {doc}`/api_reference/differentiation/index`.

## See also

- {doc}`/api_reference/differentiation/index`: differentiable simulation.
- {doc}`/api_reference/scene/scene`: the `get_state` and `reset` methods on the scene.
