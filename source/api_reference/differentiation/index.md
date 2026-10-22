# Differentiable simulation

The `genesis.grad` module provides the tensor creation ops of Genesis World. They return plain `torch.Tensor`s on `gs.device`, at the precision Genesis World runs at. For how differentiable mode works, a worked optimization example, and its limitations, see {doc}`/user_guide/theory/differentiable_simulation`.

```{toctree}
:titlesonly:

creation_ops
```

## See also

- {doc}`/user_guide/theory/differentiable_simulation`: the differentiable-simulation workflow and limitations.
- {doc}`/api_reference/engine/states/index`: the simulation state gradients flow through.
