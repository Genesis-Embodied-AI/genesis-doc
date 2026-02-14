# 可微分仿真

Genesis 支持端到端可微分物理仿真，支持通过物理引擎进行基于梯度的优化。

## 概述

可微分仿真允许你：

- 计算仿真输出相对于输入的梯度
- 通过物理优化控制策略
- 从观测中学习物理参数
- 通过多步轨迹进行反向传播

## 快速开始

```python
import genesis as gs
import torch

gs.init()

# 启用梯度追踪
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        requires_grad=True,  # 启用可微分性
    ),
)

robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# 正向仿真
initial_pos = torch.tensor([0.0, 0.0, 0.0], requires_grad=True, device=gs.device)
robot.set_dofs_position(initial_pos)

for i in range(100):
    robot.control_dofs_force(forces)
    scene.step()

# 计算损失
final_pos = robot.get_pos()
target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)
loss = torch.nn.functional.mse_loss(final_pos, target)

# 反向传播
loss.backward()

# 访问梯度
print(initial_pos.grad)
```

## 核心概念

### 启用梯度

在 `SimOptions` 中设置 `requires_grad=True`：

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        requires_grad=True,
    ),
)
```

### Genesis Tensors

Genesis 使用扩展 PyTorch tensor 的自定义 tensor：

```python
# 状态输出是 genesis tensors
pos = robot.get_pos()  # genesis.grad.Tensor

# 支持标准 PyTorch 操作
loss = (pos - target).pow(2).sum()

# 反向传播自动流经仿真
loss.backward()
```

### 梯度流

```
输入（控制、初始状态）
    ↓
正向仿真（物理步骤）
    ↓
输出（最终状态、观测）
    ↓
损失函数
    ↓
backward() 通过仿真传播
    ↓
输入梯度可用
```

## 组件

```{toctree}
:titlesonly:

tensor
creation_ops
```

## 示例：轨迹优化

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

# 优化控制序列
n_steps = 100
n_dofs = robot.n_dofs
controls = torch.zeros(n_steps, n_dofs, requires_grad=True, device=gs.device)
optimizer = torch.optim.Adam([controls], lr=0.01)

target = torch.tensor([1.0, 0.0, 0.5], device=gs.device)

for epoch in range(100):
    scene.reset()

    # 正向仿真
    for t in range(n_steps):
        robot.control_dofs_force(controls[t])
        scene.step()

    # 计算损失
    final_pos = robot.get_pos()
    loss = torch.nn.functional.mse_loss(final_pos, target)

    # 优化
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch}: loss = {loss.item():.4f}")
```

## 局限性

1. **内存**：多步轨迹需要存储中间状态
2. **并非所有操作都可微分**：某些碰撞操作可能没有梯度
3. **数值稳定性**：长时域可能存在梯度稳定性问题

## 另请参阅

- {doc}`tensor` - Genesis tensor 类
- {doc}`/api_reference/engine/states/index` - 状态管理
