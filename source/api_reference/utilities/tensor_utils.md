# Tensor Utilities

Genesis 提供用于在不同数组和张量格式之间转换的工具。

## 概述

Genesis 使用：
- **Quadrants fields**: 用于 GPU 加速物理计算
- **PyTorch tensors**: 用于状态访问和可微性
- **NumPy arrays**: 用于数据导出和可视化

## 张量转换

### 转换为 NumPy

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Get state as NumPy array
qpos = robot.get_qpos()
qpos_np = gs.utils.tensor_to_array(qpos)
print(type(qpos_np))  # numpy.ndarray
```

### 转换为 CPU

```python
# Move tensor to CPU (if on GPU)
qpos_cpu = gs.utils.tensor_to_cpu(qpos)
```

### 创建 Tensors

```python
import torch

# Create tensor on correct device
tensor = torch.zeros(10, device=gs.device, dtype=gs.tc_float)

# Or use Genesis wrapper
tensor = gs.utils.to_gs_tensor([1.0, 2.0, 3.0])
```

## 常见模式

### 获取实体状态

```python
# Returns PyTorch tensor
positions = robot.get_qpos()
velocities = robot.get_qvel()

# Convert to NumPy for processing
import numpy as np
pos_np = positions.cpu().numpy()
```

### 设置实体状态

```python
import torch

# From NumPy
target = np.array([0.1, 0.2, 0.3])
robot.set_dofs_position(torch.from_numpy(target).to(gs.device))

# From list
robot.set_dofs_position([0.1, 0.2, 0.3])
```

### Batched Tensors

使用 `n_envs > 1`：

```python
scene.build(n_envs=16)

# Batched output: (n_envs, n_dofs)
all_positions = robot.get_qpos()

# Select specific environments
some_positions = robot.get_qpos(envs_idx=[0, 5, 10])
```

## 数据类型

| Genesis | PyTorch | NumPy | Description |
|---------|---------|-------|-------------|
| `gs.tc_float` | `torch.float32` | `np.float32` | 默认 float |
| `gs.tc_int` | `torch.int32` | `np.int32` | 默认 int |

## 另请参阅

- {doc}`device` - 设备配置
- {doc}`/api_reference/engine/states/index` - 状态管理
