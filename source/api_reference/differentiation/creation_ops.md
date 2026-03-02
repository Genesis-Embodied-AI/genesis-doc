# Creation Operations

Functions for creating Genesis tensors that are compatible with differentiable simulation.

## Overview

When working with differentiable simulation, use these functions to create tensors that properly integrate with the gradient system.

## Creating Tensors

### From Python Values

```python
import genesis as gs
import torch

gs.init()

# Create tensor on correct device
tensor = torch.tensor([1.0, 2.0, 3.0], device=gs.device, dtype=gs.tc_float)

# With gradient tracking
tensor = torch.tensor(
    [1.0, 2.0, 3.0],
    device=gs.device,
    dtype=gs.tc_float,
    requires_grad=True,
)
```

### Zeros/Ones

```python
# Create zero tensor
zeros = torch.zeros(10, device=gs.device, dtype=gs.tc_float)

# Create ones tensor
ones = torch.ones(10, device=gs.device, dtype=gs.tc_float)

# With gradient tracking
zeros_grad = torch.zeros(10, device=gs.device, dtype=gs.tc_float, requires_grad=True)
```

### Random Tensors

```python
# Random uniform [0, 1)
rand = torch.rand(10, device=gs.device, dtype=gs.tc_float)

# Random normal
randn = torch.randn(10, device=gs.device, dtype=gs.tc_float)
```

## Converting to Genesis Tensors

Standard PyTorch tensors become Genesis tensors when combined with scene state:

```python
# Standard PyTorch tensor
external = torch.tensor([1.0, 2.0, 3.0], device=gs.device, requires_grad=True)

# Combine with scene state -> Genesis tensor
pos = robot.get_pos()
combined = pos + external  # Result is Genesis tensor
```

## API Reference

```{eval-rst}
.. automodule:: genesis.grad.creation_ops
   :members:
   :undoc-members:
```

## See Also

- {doc}`tensor` - Genesis Tensor class
- {doc}`index` - Differentiable simulation overview
