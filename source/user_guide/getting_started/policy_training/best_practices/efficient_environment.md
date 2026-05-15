# 🏎️ Writing an Efficient RL Environment

When thousands of environments run in parallel on a single GPU, what matters most for throughput is not what the step does, but what it doesn't do. The patterns below keep `env.step()` fully GPU-sync-free: no Python-side `.item()` / `.nonzero()` per step, no implicit host-device transfers, no buffer re-allocation.

## Pre-allocate every buffer

Allocate every tensor your `step` and `reset` will write to *once*, with the final shape and dtype. Use `torch.empty(...)` for buffers that will be overwritten each step (no reason to pay for zeroing) and `torch.zeros(...)` only when the initial value matters (e.g. accumulators).

```python
# good - allocate once
self.obs_buf = torch.empty((num_envs, num_obs), dtype=gs.tc_float, device=gs.device)
self.reset_buf = torch.ones((num_envs,), dtype=gs.tc_bool, device=gs.device)
self.episode_length_buf = torch.empty((num_envs,), dtype=gs.tc_int, device=gs.device)
```

Re-allocating inside `step` (`torch.zeros(...)` per step) drops throughput hard once env count goes up: every allocation hits the CUDA caching allocator and synchronizes against pending work.

Likewise, write into existing storage rather than replacing it:

```python
# bad - allocates a fresh tensor every step
self.commands = torch.where(reset_mask[:, None], new_commands, self.commands)

# good - writes into the existing buffer
torch.where(reset_mask[:, None], new_commands, self.commands, out=self.commands)
```

The `out=` form keeps `self.commands` pointing at the same storage, which matters when something else holds a view of it (a recorder, a logger, an observation builder). Same story for `.copy_(...)` versus `=`, and for `.masked_fill_(...)` versus `torch.where(...)` without `out=`.

## Use boolean masks for `envs_idx`

`(condition).nonzero()[:, 0]` forces a GPU sync - the host needs to know how many indices came out to materialize a 1-D tensor. **Keep `envs_idx` as a boolean mask** all the way through and feed that mask directly to Genesis APIs and to `torch.where` / `masked_fill_`.

```python
# bad - GPU sync on .nonzero()
reset_idx = self.reset_buf.nonzero()[:, 0]
self.last_actions[reset_idx] = 0.0

# good - boolean mask, no sync
self.last_actions.masked_fill_(self.reset_buf[:, None], 0.0)
```

Genesis solver and entity setters (`set_qpos`, `set_dofs_position`, `set_pos`, ...) accept a boolean mask for `envs_idx`. So does the unified `reset(envs_idx=mask)` entry point.

## Read state through zero-copy accessors

Reading entity state in the hot path is fine - *if* the accessor returns a zero-copy view into Genesis's underlying storage. The reads that support zero-copy on rigid entities, at the time of writing, are:

| Read | Returns |
|---|---|
| `entity.get_pos()` / `entity.get_quat()` | base-link world pose |
| `entity.get_vel()` / `entity.get_ang()` | base-link linear / angular velocity |
| `entity.get_dofs_position()` / `entity.get_dofs_velocity()` | per-DOF position / velocity |
| `entity.get_links_pos()` / `entity.get_links_quat()` / `entity.get_links_vel()` | per-link world poses and velocities |
| `entity.get_contacts()` | active contact set for this entity |

Any other read on the hot path likely allocates a fresh tensor; either lift it out of `step()`, or open an issue if it should be zero-copy.

For sensor outputs specifically, prefer the bulk `scene.read_sensors()` / `entity.read_sensors()` over per-sensor `sensor.read()` calls when you observe many sensors at once (one batched tensor per sensor class instead of N separate calls). It always allocates fresh storage, but the cost amortizes across every sensor of a class. See {doc}`Sensors <../../sensors/index>` for the bulk-read API.

## Reset robot state

The combination that resets a batch of envs without any GPU sync uses (a) a boolean mask for `envs_idx`, (b) the zero-copy setters with explicit pre-allocated source tensors, and (c) `skip_forward=True` so forward kinematics is computed once on the next `scene.step()` instead of inside every setter call:

```python
# `mask` is a (num_envs,) bool tensor; `init_qpos` is pre-allocated in __init__
self.robot.set_qpos(self.init_qpos, envs_idx=mask, zero_velocity=True, skip_forward=True)
self.robot.set_dofs_velocity(self.init_dof_vel, envs_idx=mask, skip_forward=True)
```

When resetting *all* environments, pass `envs_idx=None` (or omit it) - the implementation hits a faster "full overwrite" path that skips the per-env mask machinery. The recommended pattern is a single `reset(envs_idx=None | bool_mask)` entry point that branches once:

```python
def reset(self, envs_idx=None):
    self.robot.set_qpos(self.init_qpos, envs_idx=envs_idx, zero_velocity=True, skip_forward=True)

    if envs_idx is None:
        self.last_actions.zero_()
        self.episode_length_buf.zero_()
        self.reset_buf.fill_(True)
    else:
        self.last_actions.masked_fill_(envs_idx[:, None], 0.0)
        self.episode_length_buf.masked_fill_(envs_idx, 0)
        self.reset_buf.masked_fill_(envs_idx, True)
```

For coarse resets that touch every solver state at once, `scene.rigid_solver.set_state(state_idx, state, envs_idx=mask, partial=True)` is the bulk equivalent - `partial=True` is the fast path; `partial=False` resets the whole scene and is significantly slower because of the auxiliary state it has to rebuild.

Numerical blow-up (NaN positions, exploding velocities, constraint solver failure) needs to terminate the episode for *that env only*, without crashing the whole batch. The rigid solver exposes a per-env errno mask that you fold into the regular termination condition, so divergent envs are reset on the next `reset(self.reset_buf)` call with the same machinery that handles a normal episode end:

```python
self.reset_buf = self.episode_length_buf > self.max_episode_length
self.reset_buf |= torch.abs(self.base_euler[:, 1]) > self.cfg["termination_if_pitch_greater_than"]
self.reset_buf |= self.scene.rigid_solver.get_error_envs_mask()
```

## Apply commands

Command application is the other write-side hot path. The zero-copy command writers on a rigid entity are:

| Write | Effect |
|---|---|
| `entity.control_dofs_position(targets)` | PD target positions for the selected DOFs |
| `entity.control_dofs_velocity(targets)` | PD target velocities |
| `entity.control_dofs_force(forces)` | direct generalized forces |
| `entity.set_dofs_stiffness(...)` / `entity.set_dofs_damping(...)` | PD gains |
| `entity.set_dofs_velocity(vel, envs_idx=mask, skip_forward=True)` | direct velocity write |
| `entity.set_qpos(qpos, envs_idx=mask, zero_velocity=..., skip_forward=...)` | direct configuration write |

A few patterns matter when calling them:

- **Match the DOF ordering of your action vector to the entity's internal DOF order**, so you can pass a `slice(start, stop)` rather than an index tensor. Slices are free; index tensors force a gather. The Go2 example precomputes `actions_dof_idx = torch.argsort(self.motors_dof_idx)` so its policy outputs (arranged by joint name) can be permuted into slice-friendly order before the call.
- **Reuse the same target buffer across steps.** Build `target_dof_pos` into a pre-allocated tensor (`torch.empty_like(self.actions)` once at init, `out=` writes thereafter) rather than letting `actions * scale + default` produce a fresh tensor each call.
- **Don't slice the action tensor by index just to skip non-actuated DOFs.** Either include them in the policy output and write a slice, or pass a slice through `motors_dof_idx` as `slice(...)`.

