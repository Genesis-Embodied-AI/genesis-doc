# Multi-GPU simulation and training

Genesis World scales along two independent axes. Within a single GPU, a scene runs many copies of the same world at once as batched {doc}`parallel environments </user_guide/getting_started/parallel_simulation>`. Across GPUs, you launch one process per device, each running its own scene pinned to one GPU. This page covers the second axis: how to spread work over several GPUs, and how to combine it with data-parallel training.

Reach for multiple GPUs only after you have saturated one. A single modern GPU runs thousands of environments in parallel, and batching is simpler and faster than crossing a process boundary. Scale out when you need more environments than one GPU's memory holds, or when data-parallel training needs one worker per device.

Two runnable examples are the source of truth for the patterns below:

- [`examples/rigid/multi_gpu.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/multi_gpu.py): one simulation process per GPU, launched with `multiprocessing`.
- [`examples/ddp_multi_gpu.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/ddp_multi_gpu.py): data-parallel training over several GPUs with PyTorch DDP and `torchrun`.

## The one-process-per-GPU model

Genesis World does not split a single scene across GPUs. Each process initializes its own Genesis runtime, builds its own scene, and runs on exactly one device. You get multi-GPU execution by starting several such processes and pinning each to a different GPU.

Pinning happens through environment variables that must be set **before** `gs.init()` runs, because they select the device that Genesis, its compiler, and the renderer bind to at initialization:

- **`CUDA_VISIBLE_DEVICES`:** restricts which physical GPUs the CUDA runtime and PyTorch can see. Set it to a single index so the process sees exactly one device, which it then addresses as `cuda:0`.
- **`QD_VISIBLE_DEVICE`:** selects the GPU for Quadrants, the compiler that generates and runs Genesis World kernels.
- **`EGL_DEVICE_ID`:** selects the GPU used for offscreen (EGL) rendering, and only matters when the process renders images on the GPU.

Set `CUDA_VISIBLE_DEVICES` and `QD_VISIBLE_DEVICE` together to the same index so simulation and any PyTorch tensors land on one device. Because each process sees only that one GPU, it always refers to it as index `0` internally.

## Running one process per GPU

The multiprocessing example spawns a worker per GPU. Each worker sets its device variables, then runs an ordinary single-GPU Genesis program:

```python
def run(gpu_id, func):
    # Pin this process to one physical GPU before Genesis initializes.
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ["QD_VISIBLE_DEVICE"] = str(gpu_id)
    os.environ["EGL_DEVICE_ID"] = str(gpu_id)
    func()
```

```python
num_gpus = 2
processes = []
for i in range(num_gpus):
    p = multiprocessing.Process(target=run, args=(i, main))
    processes.append(p)
    p.start()
```

The body of `main()` is a normal simulation (`gs.init(backend=gs.gpu)`, build a scene, step it) with nothing GPU-index-specific in it. The isolation is entirely in the environment variables the parent sets per child.

This pattern fits embarrassingly parallel work: independent rollouts, sweeps, or data generation where the processes never need to exchange gradients. When they do, use DDP instead.

## Data-parallel training with PyTorch DDP

[`examples/ddp_multi_gpu.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/ddp_multi_gpu.py) trains a policy across GPUs with PyTorch [DistributedDataParallel](https://docs.pytorch.org/docs/stable/notes/ddp.html). Each rank owns a full Genesis scene with its own batch of environments; DDP keeps a replica of the model on each rank and averages gradients across ranks on every backward pass. The effective batch is the per-GPU `n_envs` times the number of GPUs, so adding GPUs lowers gradient noise rather than changing any single scene.

Launch it with `torchrun`, which starts one process per GPU and sets the rendezvous variables DDP reads:

```bash
torchrun --standalone --nnodes=1 --nproc_per_node=2 examples/ddp_multi_gpu.py
```

Each worker reads its rank, pins itself to the matching GPU, and seeds Genesis per rank so the environments are decorrelated across GPUs rather than identical:

```python
local_rank = int(os.environ.get("LOCAL_RANK", 0))

os.environ["CUDA_VISIBLE_DEVICES"] = str(local_rank)
os.environ["QD_VISIBLE_DEVICE"] = str(local_rank)
gs.init(backend=gs.gpu, seed=local_rank)  # distinct seed per rank
```

Build the scene and initialize the process group afterward. Because `CUDA_VISIBLE_DEVICES` already narrowed this process to one GPU, that device is `cuda:0` here and the DDP wrapper binds to it:

```python
scene.build(n_envs=args.n_envs)

gpu_id = 0
torch.cuda.set_device(gpu_id)
dist.init_process_group(backend="nccl", init_method="env://")
device = torch.device("cuda", gpu_id)

model = TinyMLP(obs_dim, act_dim).to(device)
model = DDP(model, device_ids=[gpu_id])
```

The training loop steps the simulation, reads state into a tensor, and lets DDP synchronize gradients. The observations come straight from the rigid solver's generalized coordinates, so no data leaves the GPU:

```python
for step in range(args.steps):
    scene.step()
    qpos = rigid.get_qpos()  # shape (n_envs, n_qs), on the GPU

    obs = qpos + torch.randn_like(qpos)
    logits = model(obs)
    target = qpos.sum(dim=1, keepdim=True)
    loss = torch.nn.functional.mse_loss(logits, target)

    optim.zero_grad(set_to_none=True)
    loss.backward()  # DDP averages gradients across ranks
    optim.step()
```

Shut down cleanly at the end. The barrier makes every rank reach the same point before NCCL tears down, which avoids a hang if one rank exits early:

```python
dist.barrier()
dist.destroy_process_group()
gs.destroy()
```

## Reading simulation state into tensors

On a GPU backend, entity state is already device-resident, so you can feed it to a model without a host round-trip. The DDP example reads generalized positions from the rigid solver:

```python
rigid = scene.sim.rigid_solver
qpos = rigid.get_qpos()  # shape ([n_envs,] n_qs)
```

The returned tensor carries a leading `n_envs` dimension when the scene is built with parallel environments and drops it for a single-environment scene, following the {doc}`shape convention </user_guide/getting_started/parallel_simulation>` used throughout Genesis World. After `gs.init()`, `gs.device` and `gs.backend` report the resolved PyTorch device and backend, which is useful for placing your own tensors on the same GPU.

## Notes and gotchas

:::{warning}
Set the device environment variables before `gs.init()`. They are read once at initialization; changing them afterward has no effect on the running process.
:::

:::{note}
Pinning the rendering GPU with `EGL_DEVICE_ID` is not reliable on every machine. `examples/ddp_multi_gpu.py` leaves it unset for that reason. On-GPU rendering is not required for headless simulation or training, so omit it unless you specifically render images per rank and have confirmed it works on your hardware.
:::

:::{tip}
Batch as many environments as fit on one GPU before adding a second. Watch memory with `nvidia-smi` while raising `n_envs`, and only move to multiple GPUs once a single device is full or your training recipe needs one rank per GPU.
:::

## See also

- {doc}`Parallel simulation </user_guide/getting_started/parallel_simulation>`: batching environments on one GPU, and the `([n_envs,] ...)` shape convention.
- {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>`: the single-GPU program that each process in these patterns runs.
- {doc}`Scene API </api_reference/engine/scene>`: `build`, `step`, and the `n_envs` and `env_spacing` arguments.
