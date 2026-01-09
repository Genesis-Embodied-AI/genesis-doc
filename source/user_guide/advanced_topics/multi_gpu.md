# 🖥️ Multi-GPU Simulation

Genesis supports multi-GPU execution for scaling simulations.

## Single GPU Configuration

```python
import genesis as gs

# Automatic GPU selection
gs.init(backend=gs.gpu)

# Force specific backend
gs.init(backend=gs.cuda)   # NVIDIA CUDA
gs.init(backend=gs.metal)  # Apple Metal
gs.init(backend=gs.cpu)    # CPU fallback
```

## Parallel Environments (Single GPU)

Scale by batching environments on one GPU:

```python
scene.build(n_envs=2048, env_spacing=(1.0, 1.0))
# All environments run in parallel on same GPU
```

## Multi-GPU with Multiprocessing

Run separate processes per GPU:

```python
import os
import multiprocessing

def run_simulation(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ["TI_VISIBLE_DEVICE"] = str(gpu_id)
    os.environ["EGL_DEVICE_ID"] = str(gpu_id)

    import genesis as gs
    gs.init(backend=gs.gpu)
    # ... simulation code ...

if __name__ == "__main__":
    for i in range(2):  # 2 GPUs
        p = multiprocessing.Process(target=run_simulation, args=(i,))
        p.start()
```

## Distributed Training (DDP)

Use PyTorch Distributed Data Parallel:

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

# Training loop with gradient synchronization
for step in range(steps):
    scene.step()
    loss.backward()  # DDP handles all-reduce
    optimizer.step()

dist.barrier()
dist.destroy_process_group()
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CUDA_VISIBLE_DEVICES` | PyTorch/CUDA GPU selection |
| `TI_VISIBLE_DEVICE` | Taichi GPU selection |
| `EGL_DEVICE_ID` | Rendering GPU (OpenGL/EGL) |

Always set all three together for multi-GPU setups.

## GPU Selection Patterns

| Pattern | Method | GPUs | Complexity |
|---------|--------|------|------------|
| Single GPU | `gs.init(backend=gs.gpu)` | 1 | Low |
| Batched envs | `scene.build(n_envs=N)` | 1 | Low |
| Multi-process | Multiprocessing + env vars | N | Medium |
| Distributed | torchrun + DDP | N | High |

## Best Practices

1. **Batch first**: Use large `n_envs` on single GPU before scaling to multi-GPU
2. **Set all env vars**: Always set CUDA, Taichi, and EGL device together
3. **Synchronize DDP**: Call `dist.barrier()` before destroying process groups
4. **Headless rendering**: Set `pyglet.options["headless"] = True` on servers
5. **Monitor memory**: Use `nvidia-smi` during batched simulation

## Device Access

After initialization:

```python
gs.device    # PyTorch device (e.g., "cuda:0", "mps:0")
gs.backend   # Backend type (gs.cuda, gs.metal, gs.cpu)
```
