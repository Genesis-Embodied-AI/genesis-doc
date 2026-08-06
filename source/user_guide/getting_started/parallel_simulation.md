# Parallel simulation

```{figure} ../../_static/images/parallel_sim.png
:alt: A grid of Franka arms, each one a separate simulated environment running in parallel.
```

Training a policy takes millions of interaction steps, so you want many environments running at once. This tutorial runs many copies of a scene simultaneously on the GPU. The runnable script is [`examples/tutorials/parallel_simulation.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/parallel_simulation.py).

## Why parallelism matters

A GPU has thousands of cores, and stepping a single Franka arm leaves almost all of them idle. Genesis World steps many identical copies of a scene at once instead, so one pass of the physics kernels advances the whole batch.

We call one copy of the scene an **environment** (**env**) and count them with `n_envs`, following the learning literature, which calls the parallelism itself **batching**. Describe the plane and the Franka arm exactly as in {doc}`hello_genesis`, then choose the number of copies when you build the scene.

## Building parallel environments

Initialize on a GPU backend, so the batch has the cores to fill:

```python
gs.init(backend=gs.gpu)
```

Scene creation and entity loading are unchanged. The only line that differs is `scene.build()`, which takes the number of environments:

```python
# create 20 parallel environments
B = 20
scene.build(n_envs=B, env_spacing=(1.0, 1.0))
```

- `n_envs` is the batch size. With `n_envs=0` (the default) the scene has no batch dimension; with `n_envs > 0`, every state you set or read carries a leading batch dimension of that size.
- `env_spacing` is a `(x, y)` offset in meters that lays the environments out on a grid in the viewer. It affects visualization only, so every environment starts from the same state at the same simulated position.

The environments are independent: each has its own copy of every entity's state, and stepping the scene advances all of them together with one `scene.step()` call.

## Batched tensor shapes

Once the scene is built with `n_envs > 0`, every per-environment quantity gains a leading batch dimension. Genesis World documents this with the bracket notation `([n_envs,] ...)`, where the bracketed dimension is present only when the scene is batched. For the Franka arm, which has 9 **dofs** (degrees of freedom):

```python
q = franka.get_dofs_position()  # shape ([n_envs,] n_dofs) -> (20, 9) here
```

The same rule applies to the commands you send. `control_dofs_position` expects a target of shape `([n_envs,] n_dofs)`, so to drive all 20 arms to the same joint configuration, tile a single 9-dof pose across the batch:

```python
# control all the robots
franka.control_dofs_position(
    torch.tile(torch.tensor([0, 0, 0, -1.0, 0, 1.0, 0, 0.02, 0.02], device=gs.device), (B, 1)),
)
```

Because the simulation runs on the GPU, build these tensors directly on `gs.device`. `gs.device` is the Torch device Genesis World selected during `gs.init()`. Keeping data there avoids copying between host and device on every step, which is the dominant cost at large batch sizes. NumPy arrays also work, but incur that transfer.

## Controlling a subset of environments

To act on only some environments, pass `envs_idx`. The batch dimension of the command must then match the number of selected environments, not `n_envs`:

```python
# control only 3 environments: 1, 5, and 7.
franka.control_dofs_position(
    position=torch.zeros(3, 9, device=gs.device),
    envs_idx=torch.tensor([1, 5, 7], device=gs.device),
)
```

The same `envs_idx` argument is available on the state-reading methods (for example `get_dofs_position`) and on the other `control_dofs_*` and `set_dofs_*` methods, so you can reset or query individual environments, the typical pattern when environments finish episodes at different times during training.

## Scaling up

Genesis World supports tens of thousands of environments on a single GPU. Turn off the viewer for headless throughput and raise `n_envs`; memory use grows with the batch, so reduce it if your GPU runs out of VRAM. To measure throughput on your own hardware, use the scripts in [`examples/speed_benchmark`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/speed_benchmark) and see {doc}`/user_guide/developers/profiling`.

:::{tip}
Genesis World prints the real-time simulation speed (FPS) to the terminal by default. Pass `profiling_options=gs.options.ProfilingOptions(show_FPS=False)` to `gs.Scene` to quiet it.
:::

## See also

- {doc}`hello_genesis`: the single-environment scene this tutorial parallelizes.
- {doc}`control_your_robot`: the full set of `control_dofs_*` and `set_dofs_*` methods, all of which accept a batch dimension and `envs_idx`.
