# States

States in Genesis World hold the runtime data for physics simulation, including positions, velocities, forces, and other solver-specific variables.

## Overview

`scene.get_state()` returns a `SimState`, the aggregate snapshot for the whole scene. It holds one per-solver state for each solver present:

- **RigidSolverState**: link poses, joint positions and velocities
- **MPMSolverState**: particle positions, velocities, deformation gradients
- **FEMSolverState**: node positions, velocities
- **PBDSolverState**: particle positions, velocities
- **SPHSolverState**: particle positions, velocities, densities

## Accessing state

States are accessed through entities or the simulator:

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Access via entity
positions = robot.get_qpos()      # Joint positions
velocities = robot.get_qvel()     # Joint velocities
link_pos = robot.get_link("ee").get_pos()

# Full state access (advanced)
rigid_solver = scene.sim.rigid_solver
# ... direct solver state access
```

## State for parallel environments

With `n_envs > 1`, states are batched:

```python
scene.build(n_envs=16)

# Batched state access
positions = robot.get_qpos()  # Shape: (n_envs, n_dofs)

# Per-environment access
positions = robot.get_qpos(envs_idx=[0, 5, 10])
```

## State management

### Saving state

```python
state = scene.get_state()  # a SimState snapshot of the whole scene
```

### Restoring state

The scene has no `set_state`. Restore a saved `SimState` by passing it to `scene.reset`, which resets the scene to that state and registers it as the new initial state:

```python
scene.reset(state=state)
```

Individual solvers and entities expose their own `set_state` for finer-grained restoration (for example, `scene.sim.rigid_solver.set_state(...)`).

### Resetting

```python
scene.reset()  # reset all environments to the initial state
scene.reset(envs_idx=[0, 1, 2])  # reset specific environments
```

## Gradient tracking

For differentiable simulation:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        requires_grad=True,
    ),
)

# States now track gradients
scene.step()
loss = compute_loss(robot.get_qpos())
loss.backward()
```

## See also

- {doc}`/api_reference/differentiation/index`: differentiable simulation
- {doc}`/api_reference/scene/scene`: scene state methods (`get_state`, `reset`)
