# States

A state holds the runtime data of a simulation: positions, velocities, forces, and the solver-specific variables that evolve each step. `scene.get_state()` returns a `SimState`, an aggregate snapshot of the whole scene that holds one per-solver state for each active solver:

- **RigidSolverState:** link poses, joint positions and velocities.
- **MPMSolverState:** particle positions, velocities, deformation gradients.
- **FEMSolverState:** node positions, velocities.
- **PBDSolverState:** particle positions, velocities.
- **SPHSolverState:** particle positions, velocities, densities.

## Reading state

Read state through the entity you added, rather than through the aggregate snapshot. After `scene.build()`, call the getters directly:

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

qpos = robot.get_qpos()                 # ([n_envs,] n_dofs)
qvel = robot.get_qvel()                 # ([n_envs,] n_dofs)
ee_pos = robot.get_link("ee").get_pos()  # ([n_envs,] 3)
```

The returned tensors follow the batched-optional shape convention: the leading environment dimension is present when the scene is built with multiple environments and absent otherwise. Pass `envs_idx` to read a subset:

```python
scene.build(n_envs=16)
qpos = robot.get_qpos()                  # (16, n_dofs)
qpos = robot.get_qpos(envs_idx=[0, 5, 10])  # (3, n_dofs)
```

See {doc}`/user_guide/configuration/conventions` for the full shape and dtype conventions.

## Saving and restoring

`scene.get_state()` returns a `SimState` snapshot of the whole scene:

```python
state = scene.get_state()
```

The scene has no `set_state`. Restore a snapshot by passing it to `scene.reset`, which resets the scene to that state and registers it as the new initial state:

```python
scene.reset(state=state)   # restore a saved snapshot
scene.reset()              # reset all environments to the initial state
scene.reset(envs_idx=[0, 1, 2])  # reset only the given environments
```

Individual solvers and entities expose their own `set_state` for finer-grained restoration, for example `scene.sim.rigid_solver.set_state(...)`.

## Gradient tracking

When the scene is built for differentiable simulation, state tensors track gradients, so a loss computed from them can be backpropagated:

```python
scene = gs.Scene(sim_options=gs.options.SimOptions(requires_grad=True))
# ... build, step ...
loss = compute_loss(robot.get_qpos())
loss.backward()
```

## See also

- {doc}`/api_reference/differentiation/index`: differentiable simulation.
- {doc}`/api_reference/scene/scene`: the `get_state` and `reset` methods on the scene.
