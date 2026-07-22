# Tensor

`genesis.grad.Tensor` extends `torch.Tensor` with a link to the scene it came from, which is what lets a loss computed from scene state backpropagate through the physics. State getters (`get_pos()`, `get_vel()`, `get_qpos()`, ...) return it when the scene is built with `requires_grad=True`. For the workflow, see {doc}`/user_guide/theory/differentiable_simulation`.

```{eval-rst}
.. autoclass:: genesis.grad.tensor.Tensor
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/theory/differentiable_simulation`: the differentiable-simulation workflow.
- {doc}`creation_ops`: creating tensors for differentiable simulation.
