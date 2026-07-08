# Writing an efficient RL environment

When thousands of environments run in parallel on one GPU, throughput is decided less by what `env.step()` computes than by what it forces the GPU to stop and wait for. A step that runs a batched physics kernel over `n_envs` states is fast; the same step becomes slow the moment it copies a value back to the CPU, allocates a fresh tensor, or loops in Python over environments. This page explains that performance model and the patterns that keep the step loop on the device.

The reference environment throughout is the quadruped locomotion example, [`examples/locomotion/go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py). It builds `n_envs` copies of a Go2 robot (see {doc}`/user_guide/getting_started/parallel_simulation` for how batched builds work) and its `step` is written to run without a single host-device synchronization.

## The performance model

Genesis World runs its physics on the GPU. Your environment code runs in Python on the CPU and issues work to the GPU asynchronously: `scene.step()` and every tensor operation queue up and return immediately, before the GPU has finished. Three things break that pipeline, and all three cost throughput that faster physics cannot win back.

- **Host-device synchronization:** any operation that needs a tensor's value on the CPU (`.item()`, `.cpu()`, `.tolist()`, `bool(t)`, `print(t)`, or `.nonzero()`, which returns a dynamically sized tensor) blocks the CPU until the GPU drains its entire queue. One such call per step, times thousands of steps, dominates the wall clock.
- **Allocation:** creating a tensor inside the loop (`torch.zeros(...)`, `torch.tensor(...)`, most fresh reads) goes through the CUDA caching allocator, which synchronizes against pending work when it has to find or free memory.
- **Python overhead:** a `for` loop over environments issues `n_envs` times the kernel launches for the same result a single batched op produces. The fixed per-launch cost, not the arithmetic, is what you pay.

The rule that follows: operate on whole `([n_envs,] ...)` tensors at once, keep every tensor on the device, and never let a value cross back to the host inside the step loop.

## Keep tensors on the device

Allocate every buffer on Genesis World's device and with its dtypes, so nothing is implicitly moved or cast later. `gs.device` is the active backend's device, and `gs.tc_float`, `gs.tc_int`, and `gs.tc_bool` are the torch dtypes that match the precision chosen at `gs.init`.

```python
self.base_lin_vel = torch.empty((self.num_envs, 3), dtype=gs.tc_float, device=gs.device)
self.reset_buf = torch.ones((self.num_envs,), dtype=gs.tc_bool, device=gs.device)
self.episode_length_buf = torch.empty((self.num_envs,), dtype=gs.tc_int, device=gs.device)
```

Read entity state through the batched accessors rather than pulling it out to inspect it. Each returns a device tensor of shape `([n_envs,] ...)` that you feed straight into the next operation:

```python
self.base_pos = self.robot.get_pos()                          # shape (n_envs, 3)
self.dof_pos = self.robot.get_dofs_position(self.motors_dof_idx)  # shape (n_envs, n_motors)
self.dof_vel = self.robot.get_dofs_velocity(self.motors_dof_idx)
```

The common rigid-entity reads used on the hot path are `get_pos` / `get_quat` (base-link world pose), `get_vel` / `get_ang` (base-link linear and angular velocity), and `get_dofs_position` / `get_dofs_velocity` (per-dof state). For sensor outputs, prefer the bulk `scene.read_sensors()` or `entity.read_sensors()` over per-sensor `sensor.read()` when you observe many sensors at once: one batched tensor per sensor class amortizes better than N separate calls.

## Pre-allocate buffers, write in place

Allocate every tensor `step` and `reset` will write to once, in `__init__`, at final shape and dtype. Use `torch.empty(...)` for buffers you overwrite each step, since there is no reason to pay for zeroing, and `torch.zeros(...)` only where the initial value matters, such as accumulators.

Thereafter, write into the existing storage instead of replacing it. In-place operations avoid the per-step allocation and keep the tensor's identity stable, which matters when a logger, recorder, or observation builder holds a view of it.

- **`buf.zero_()` / `buf.fill_(x)`:** reset a buffer in place.
- **`dst.copy_(src)`:** overwrite `dst` without allocating.
- **`buf.masked_fill_(mask, x)`:** write `x` where a boolean mask is true.
- **`torch.where(mask, a, b, out=dst)`:** select into an existing tensor rather than returning a new one.

The Go2 reward accumulation shows the pattern: `rew_buf` is zeroed in place, then each reward term adds into it. The loop is over reward *terms*, a handful of them, not over environments, and each term is itself a batched op over all `n_envs`.

```python
self.rew_buf.zero_()
for name, reward_func in self.reward_functions.items():
    rew = reward_func() * self.reward_scales[name]
    self.rew_buf += rew
    self.episode_sums[name] += rew
```

## Use boolean masks for `envs_idx`, not index tensors

Termination is the classic place a sync sneaks in. Computing which environments to reset with `(condition).nonzero()` forces a sync, because the host must learn how many indices came out to size the result. Keep the selection as a boolean mask of shape `(n_envs,)` the whole way through: build it with batched comparisons, combine conditions with `|=`, and pass it directly to the setters.

```python
self.reset_buf = self.episode_length_buf > self.max_episode_length
self.reset_buf |= torch.abs(self.base_euler[:, 1]) > self.env_cfg["termination_if_pitch_greater_than"]
self.reset_buf |= torch.abs(self.base_euler[:, 0]) > self.env_cfg["termination_if_roll_greater_than"]
self.reset_buf |= self.scene.rigid_solver.get_error_envs_mask()
```

The last line folds in numerical divergence. When the solver hits a NaN or a constraint failure in some environment, `scene.rigid_solver.get_error_envs_mask()` returns a `(n_envs,)` boolean mask of the affected environments. Reset those with the same machinery as a normal episode end, so a single diverged environment terminates on its own instead of crashing the batch.

Genesis World setters and the solver accept a boolean `envs_idx` mask directly, so you never have to materialize indices to use one.

## Reset a batch without syncing

Reset writes the initial state into the selected environments. The sync-free combination is a boolean `envs_idx` mask, pre-allocated source tensors, and two keyword flags on the setter:

```python
self.robot.set_qpos(self.init_qpos, envs_idx=envs_idx, zero_velocity=True, skip_forward=True)
```

- **`zero_velocity=True`:** clears velocities as part of the same write, instead of a second setter call.
- **`skip_forward=True`:** defers forward kinematics so it runs once on the next `scene.step()`, rather than inside every setter call during reset.

Branch once on whether this is a full or partial reset. When resetting *all* environments, pass `envs_idx=None`; the implementation takes a faster full-overwrite path and you can use the cheaper `zero_()` / `fill_()` on your own buffers instead of masked writes.

```python
if envs_idx is None:
    self.actions.zero_()
    self.episode_length_buf.zero_()
    self.reset_buf.fill_(True)
else:
    self.actions.masked_fill_(envs_idx[:, None], 0.0)
    self.episode_length_buf.masked_fill_(envs_idx, 0)
    self.reset_buf.masked_fill_(envs_idx, True)
```

For a coarse reset that restores every solver state at once, `scene.rigid_solver.set_state(f, state, envs_idx=mask, partial=True)` is the bulk equivalent. Keep `partial=True`: `partial=False` rebuilds the whole scene's auxiliary state and is significantly slower.

## Apply commands efficiently

Control application is the write-side hot path. The Go2 policy outputs one action per actuated joint, scales it, and offsets by the default pose to get position targets:

```python
target_dof_pos = exec_actions * self.env_cfg["action_scale"] + self.default_dof_pos
self.robot.control_dofs_position(target_dof_pos[:, self.actions_dof_idx], slice(6, 18))
```

Two details keep this cheap.

- **Address dofs with a `slice`, not an index tensor.** The third argument to `control_dofs_position` selects which dofs to drive. A `slice(6, 18)` is a free view; an index tensor forces a gather. Go2 arranges its actuated dofs contiguously and precomputes `actions_dof_idx = torch.argsort(self.motors_dof_idx)` once at init, so policy outputs ordered by joint name can be permuted into that contiguous layout before the call.
- **Reuse the target buffer where you can.** Every `a * scale + b` allocates a fresh tensor. Where a buffer's identity must stay stable, build the target into a pre-allocated tensor with `out=` writes instead. (Operations that change shape, such as `torch.concatenate` when assembling an observation vector, necessarily allocate; that is an accepted exception, not a rule to fight.)

The zero-copy command writers on a rigid entity are `control_dofs_position`, `control_dofs_velocity`, and `control_dofs_force` for PD targets and direct forces, and `set_dofs_position` / `set_dofs_velocity` / `set_qpos` for direct state writes.

## Turn on performance mode for training

Once the environment is finalized, `gs.init(performance_mode=True)` bakes the now-static tensor shapes into the compiled kernels for roughly 30% faster simulation. The cost is that any change to the scene triggers a recompile that can take several minutes. Leave it off for research, debugging, and interactive work; turn it on for long training and production runs, where the scene is fixed and the one-time recompile pays for itself. See {doc}`/user_guide/getting_started/hello_genesis` for the other `gs.init` options.

## Verify with the profiler

Do not guess where the syncs are. Attach the PyTorch profiler around a few steps and look for gaps between kernel launches, which are the CPU waiting on the GPU. See {doc}`/user_guide/developers/profiling` for the profiling setup and how to read Quadrants kernel timings.

## See also

- {doc}`/user_guide/getting_started/parallel_simulation`: how batched builds and `n_envs` work.
- {doc}`domain_randomization`: vary physics across environments without breaking the sync-free step.
- {doc}`/user_guide/developers/profiling`: measure kernel time and launch latency.
