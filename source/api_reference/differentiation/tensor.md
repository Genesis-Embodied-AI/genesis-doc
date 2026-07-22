# `Tensor`

The `genesis.grad.Tensor` class extends `torch.Tensor` to support end-to-end gradient flow through Genesis World simulations.

## Overview

Genesis World Tensors:

- Extend PyTorch tensors with scene tracking
- Enable automatic gradient propagation through physics
- Support all standard PyTorch operations
- Track parent tensors for gradient flow

## Behavior

State getters such as `robot.get_pos()`, `robot.get_vel()`, and `robot.get_qpos()` return a `genesis.grad.Tensor` when the scene is built with `requires_grad=True`. It behaves like a `torch.Tensor` in every operation and additionally carries a link to the scene it came from, which is what lets `loss.backward()` flow gradients through the physics.

To stop gradients flowing back into the simulation, use `tensor.detach()` (which drops the scene link by default) or `tensor.sceneless()` (which keeps autograd but drops only the scene link). Read `tensor.scene` to see which scene, if any, a tensor is bound to. For the end-to-end differentiable workflow, see {doc}`index`.

## API reference

```{eval-rst}
.. autoclass:: genesis.grad.tensor.Tensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: Differentiable simulation overview
- {doc}`creation_ops`: Creating tensors
