# Tensor

The `genesis.grad.Tensor` class extends `torch.Tensor` to support end-to-end gradient flow through Genesis simulations.

## Overview

Genesis Tensors:

- Extend PyTorch tensors with scene tracking
- Enable automatic gradient propagation through physics
- Support all standard PyTorch operations
- Track parent tensors for gradient flow

## Usage

Genesis Tensors are automatically created when you access state:

```python
import genesis as gs
import torch

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        requires_grad=True,
    ),
)

robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# These return genesis.grad.Tensor
pos = robot.get_pos()       # Genesis Tensor
vel = robot.get_vel()       # Genesis Tensor
qpos = robot.get_qpos()     # Genesis Tensor
```

## Gradient Flow

```python
# Forward pass
scene.step()
pos = robot.get_pos()

# Compute loss
target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)
loss = (pos - target).pow(2).sum()

# Backward pass - flows through simulation
loss.backward()
```

## Detaching from Scene

To prevent gradients from flowing through the simulation:

```python
# Detach and remove scene tracking
pos_detached = pos.detach(sceneless=True)

# Or explicitly
pos_sceneless = pos.sceneless()
```

## Checking Scene Association

```python
# Check if tensor is associated with a scene
if pos.scene is not None:
    print(f"Tensor from scene: {pos.scene.uid}")
```

## API Reference

```{eval-rst}
.. autoclass:: genesis.grad.Tensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Differentiable simulation overview
- {doc}`creation_ops` - Creating tensors
