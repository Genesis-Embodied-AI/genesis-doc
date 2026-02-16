# 🖥️ 多 GPU 仿真

Genesis 支持多 GPU 执行以扩展仿真。

## 单 GPU 配置

```python
import genesis as gs

# 自动 GPU 选择
gs.init(backend=gs.gpu)

# 强制特定后端
gs.init(backend=gs.cuda)   # NVIDIA CUDA
gs.init(backend=gs.metal)  # Apple Metal
gs.init(backend=gs.cpu)    # CPU 回退
```

## 并行环境（单 GPU）

通过在单个 GPU 上批处理环境来扩展：

```python
scene.build(n_envs=2048, env_spacing=(1.0, 1.0))
# 所有环境在同一 GPU 上并行运行
```

## 使用多进程的多 GPU

每 GPU 运行单独的进程：

```python
import os
import multiprocessing

def run_simulation(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ["TI_VISIBLE_DEVICE"] = str(gpu_id)
    os.environ["EGL_DEVICE_ID"] = str(gpu_id)

    import genesis as gs
    gs.init(backend=gs.gpu)
    # ... 仿真代码 ...

if __name__ == "__main__":
    for i in range(2):  # 2 个 GPU
        p = multiprocessing.Process(target=run_simulation, args=(i,))
        p.start()
```

## 分布式训练 (DDP)

使用 PyTorch 分布式数据并行：

```bash
torchrun --standalone --nnodes=1 --nproc_per_node=2 train.py
```

```python
import os
import torch
import torch.distributed as dist
import genesis as gs

local_rank = int(os.environ.get("LOCAL_RANK", 0))
os.environ["CUDA_VISIBLE_DEVICES"] = str(local_rank)
os.environ["TI_VISIBLE_DEVICE"] = str(local_rank)

gs.init(backend=gs.gpu, seed=local_rank)
scene.build(n_envs=2048)

torch.cuda.set_device(0)
dist.init_process_group(backend="nccl", init_method="env://")
model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[0])

# 带梯度同步的训练循环
for step in range(steps):
    scene.step()
    loss.backward()  # DDP 处理 all-reduce
    optimizer.step()

dist.barrier()
dist.destroy_process_group()
```

## 环境变量

| 变量 | 目的 |
|----------|---------|
| `CUDA_VISIBLE_DEVICES` | PyTorch/CUDA GPU 选择 |
| `TI_VISIBLE_DEVICE` | Taichi GPU 选择 |
| `EGL_DEVICE_ID` | 渲染 GPU (OpenGL/EGL) |

对于多 GPU 设置，始终同时设置所有三个。

## GPU 选择模式

| 模式 | 方法 | GPU | 复杂度 |
|---------|--------|------|------------|
| 单 GPU | `gs.init(backend=gs.gpu)` | 1 | 低 |
| 批处理环境 | `scene.build(n_envs=N)` | 1 | 低 |
| 多进程 | 多进程 + 环境变量 | N | 中 |
| 分布式 | torchrun + DDP | N | 高 |

## 最佳实践

1. **优先批处理**：在扩展到多 GPU 之前，先在单个 GPU 上使用大的 `n_envs`
2. **设置所有环境变量**：始终同时设置 CUDA、Taichi 和 EGL 设备
3. **同步 DDP**：在销毁进程组之前调用 `dist.barrier()`
4. **无头渲染**：在服务器上设置 `pyglet.options["headless"] = True`
5. **监控内存**：在批处理仿真期间使用 `nvidia-smi`

## 设备访问

初始化后：

```python
gs.device    # PyTorch 设备 (例如 "cuda:0", "mps:0")
gs.backend   # 后端类型 (gs.cuda, gs.metal, gs.cpu)
```
