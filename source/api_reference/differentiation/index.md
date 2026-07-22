# Differentiable simulation

The `genesis.grad` module provides the gradient-carrying tensor type and creation ops used when the scene is built with `requires_grad=True`. For how differentiable mode works, a worked optimization example, and its limitations, see {doc}`/user_guide/theory/differentiable_simulation`.

```{toctree}
:titlesonly:

tensor
creation_ops
```

## See also

- {doc}`/user_guide/theory/differentiable_simulation`: the differentiable-simulation workflow and limitations.
- {doc}`/api_reference/engine/states/index`: the simulation state gradients flow through.
