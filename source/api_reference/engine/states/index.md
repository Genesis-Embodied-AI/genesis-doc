# States

States in Genesis hold the runtime data for physics simulation, including positions, velocities, forces, and other solver-specific variables.

## Overview

Each solver maintains its own state:

- **RigidState**: Link poses, joint positions/velocities
- **MPMState**: Particle positions, velocities, deformation gradients
- **FEMState**: Node positions, velocities
- **PBDState**: Particle positions, velocities
- **SPHState**: Particle positions, velocities, densities

## Accessing State

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

## State for Parallel Environments

With `n_envs > 1`, states are batched:

```python
scene.build(n_envs=16)

# Batched state access
positions = robot.get_qpos()  # Shape: (n_envs, n_dofs)

# Per-environment access
positions = robot.get_qpos(envs_idx=[0, 5, 10])
```

## State Management

### Saving State

```python
state = scene.get_state()
```

### Restoring State

```python
scene.set_state(state)
```

### Resetting

```python
scene.reset()  # Reset all environments
scene.reset(envs_idx=[0, 1, 2])  # Reset specific environments
```

## Gradient Tracking

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

## See Also

- {doc}`/api_reference/differentiation/index` - Differentiable simulation
- {doc}`/api_reference/scene/scene` - Scene state methods
