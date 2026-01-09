# Differentiable Simulation

Genesis supports end-to-end differentiable physics simulation, enabling gradient-based optimization through the physics engine.

## Overview

Differentiable simulation allows you to:

- Compute gradients of simulation outputs with respect to inputs
- Optimize control policies through physics
- Learn physical parameters from observations
- Backpropagate through multi-step trajectories

## Quick Start

```python
import genesis as gs
import torch

gs.init()

# Enable gradient tracking
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        requires_grad=True,  # Enable differentiability
    ),
)

robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Forward simulation
initial_pos = torch.tensor([0.0, 0.0, 0.0], requires_grad=True, device=gs.device)
robot.set_dofs_position(initial_pos)

for i in range(100):
    robot.control_dofs_force(forces)
    scene.step()

# Compute loss
final_pos = robot.get_pos()
target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)
loss = torch.nn.functional.mse_loss(final_pos, target)

# Backward pass
loss.backward()

# Access gradients
print(initial_pos.grad)
```

## Key Concepts

### Enabling Gradients

Set `requires_grad=True` in `SimOptions`:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        requires_grad=True,
    ),
)
```

### Genesis Tensors

Genesis uses custom tensors that extend PyTorch tensors:

```python
# State outputs are genesis tensors
pos = robot.get_pos()  # genesis.grad.Tensor

# Supports standard PyTorch operations
loss = (pos - target).pow(2).sum()

# Backward automatically flows through simulation
loss.backward()
```

### Gradient Flow

```
Input (controls, initial state)
    ↓
Forward simulation (physics steps)
    ↓
Output (final state, observations)
    ↓
Loss function
    ↓
backward() propagates through simulation
    ↓
Input gradients available
```

## Components

```{toctree}
:titlesonly:

tensor
creation_ops
```

## Example: Trajectory Optimization

```python
import genesis as gs
import torch

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        requires_grad=True,
    ),
)

robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Optimize control sequence
n_steps = 100
n_dofs = robot.n_dofs
controls = torch.zeros(n_steps, n_dofs, requires_grad=True, device=gs.device)
optimizer = torch.optim.Adam([controls], lr=0.01)

target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)

for epoch in range(100):
    scene.reset()

    # Forward simulation
    for t in range(n_steps):
        robot.control_dofs_force(controls[t])
        scene.step()

    # Compute loss
    final_pos = robot.get_pos()
    loss = torch.nn.functional.mse_loss(final_pos, target)

    # Optimize
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}: loss = {loss.item():.4f}")
```

## Limitations

1. **Memory**: Multi-step trajectories require storing intermediate states
2. **Not all operations differentiable**: Some collision operations may not have gradients
3. **Numerical stability**: Long horizons may have gradient stability issues

## See Also

- {doc}`tensor` - Genesis tensor class
- {doc}`/api_reference/engine/states/index` - State management
