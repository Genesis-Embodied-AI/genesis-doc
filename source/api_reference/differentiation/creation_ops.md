# 创建操作

用于创建与可微分仿真兼容的 Genesis tensors 的函数。

## 概述

在使用可微分仿真时，使用这些函数创建与梯度系统正确集成的 tensors。

## 创建 Tensors

### 从 Python 值创建

```python
import genesis as gs
import torch

gs.init()

# 在正确的设备上创建 tensor
tensor = torch.tensor([1.0, 2.0, 3.0], device=gs.device, dtype=gs.tc_float)

# 启用梯度追踪
tensor = torch.tensor(
    [1.0, 2.0, 3.0],
    device=gs.device,
    dtype=gs.tc_float,
    requires_grad=True,
)
```

### 零/一 Tensors

```python
# 创建零 tensor
zeros = torch.zeros(10, device=gs.device, dtype=gs.tc_float)

# 创建一 tensor
ones = torch.ones(10, device=gs.device, dtype=gs.tc_float)

# 启用梯度追踪
zeros_grad = torch.zeros(10, device=gs.device, dtype=gs.tc_float, requires_grad=True)
```

### 随机 Tensors

```python
# 随机均匀分布 [0, 1)
rand = torch.rand(10, device=gs.device, dtype=gs.tc_float)

# 随机正态分布
randn = torch.randn(10, device=gs.device, dtype=gs.tc_float)
```

## 转换为 Genesis Tensors

标准 PyTorch tensors 在与 scene state 结合时会变成 Genesis tensors：

```python
# 标准 PyTorch tensor
external = torch.tensor([1.0, 2.0, 3.0], device=gs.device, requires_grad=True)

# 与 scene state 结合 -> Genesis tensor
pos = robot.get_pos()
combined = pos + external  # 结果是 Genesis tensor
```

## API 参考

```{eval-rst}
.. automodule:: genesis.grad.creation_ops
   :members:
   :undoc-members:
```

## 另请参阅

- {doc}`tensor` - Genesis Tensor 类
- {doc}`index` - 可微分仿真概述
