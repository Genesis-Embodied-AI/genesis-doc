# Tensor

`genesis.grad.Tensor` 类扩展了 `torch.Tensor`，以支持通过 Genesis 仿真的端到端梯度流。

## 概述

Genesis Tensors：

- 通过 scene tracking 扩展 PyTorch tensors
- 支持通过物理的自动梯度传播
- 支持所有标准 PyTorch 操作
- 追踪父 tensors 以实现梯度流

## 用法

当您访问状态时，Genesis Tensors 会自动创建：

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

# 这些返回 genesis.grad.Tensor
pos = robot.get_pos()       # Genesis Tensor
vel = robot.get_vel()       # Genesis Tensor
qpos = robot.get_qpos()     # Genesis Tensor
```

## 梯度流

```python
# 正向传播
scene.step()
pos = robot.get_pos()

# 计算损失
target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)
loss = (pos - target).pow(2).sum()

# 反向传播 - 流经仿真
loss.backward()
```

## 从 Scene 分离

要阻止梯度流经仿真：

```python
# 分离并移除 scene tracking
pos_detached = pos.detach(sceneless=True)

# 或显式地
pos_sceneless = pos.sceneless()
```

## 检查 Scene 关联

```python
# 检查 tensor 是否与 scene 关联
if pos.scene is not None:
    print(f"Tensor from scene: {pos.scene.uid}")
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.grad.Tensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 可微分仿真概述
- {doc}`creation_ops` - 创建 tensors
