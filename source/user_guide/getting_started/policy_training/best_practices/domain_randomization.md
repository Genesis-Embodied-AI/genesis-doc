# Domain randomization

A policy trained in a single, fixed simulation learns the quirks of that exact simulation. On real hardware, where friction, link masses, and actuator gains differ from your model and drift over time, that policy fails. **Domain randomization** closes the gap: you sample a different set of physical and task parameters for each parallel environment, so the policy sees a distribution of dynamics during training and learns behavior that is robust to any single realization.

Genesis World is built for this. Because the simulation is already batched across environments, randomizing per-environment parameters is a matter of passing a tensor with a leading `n_envs` dimension. This page covers what you can randomize, the batched APIs that set it, and when to apply each kind of randomization.

Two randomization patterns recur in reinforcement learning, and they differ in *when* you apply them:

- **Per-run physics randomization:** properties that describe the robot and its contacts, such as friction, mass, and PD gains. Set these once, right after `scene.build()`, so each environment simulates a slightly different body for the whole run.
- **Per-episode task randomization:** quantities that reset with the episode, such as velocity commands, spawn poses, and reset states. Resample these inside your environment's reset, restricted to the environments that just terminated.

## Randomizing physics per environment

The rigid entity exposes batched setters for the properties that most affect sim-to-real transfer. Each accepts a tensor whose leading dimension is `n_envs`, so one call assigns a distinct value to every environment. The following excerpt is from [`examples/rigid/domain_randomization.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/domain_randomization.py), which loads a Go2 quadruped and randomizes it across eight environments:

```python
scene.build(n_envs=8)

# Scale each link's friction by a per-env, per-link factor in [0.5, 1.5).
robot.set_friction_ratio(
    friction_ratio=0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=np.arange(0, robot.n_links),
)

# Perturb each link's mass by a per-env offset in [-0.5, 0.5) kg.
robot.set_mass_shift(
    mass_shift=-0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=np.arange(0, robot.n_links),
)

# Shift each link's center of mass by up to 5 cm on each axis.
robot.set_COM_shift(
    com_shift=-0.05 + 0.1 * torch.rand(scene.n_envs, robot.n_links, 3),
    links_idx_local=np.arange(0, robot.n_links),
)
```

The three methods differ in what they modify:

- **`set_friction_ratio`:** multiplies each geom's base friction coefficient by the supplied factor, shape `(n_envs, n_links)`. It scales rather than replaces, so a ratio of `1.0` leaves the model's friction unchanged. To set an absolute coefficient for the whole entity instead, use `set_friction(friction)`, which takes a single float and requires it in the range `[1e-2, 5.0]` for stability.
- **`set_mass_shift`:** adds a mass offset in kg to each link, shape `(n_envs, n_links)`. It is an additive shift on top of the model's mass, not a replacement.
- **`set_COM_shift`:** adds a center-of-mass offset in meters to each link, shape `(n_envs, n_links, 3)`, in the link's local frame.

These three write to per-environment state buffers, so they work whether or not the scene batches its static model info. Pass `envs_idx` to any of them to restrict the update to a subset of environments.

## Randomizing actuator gains

Randomizing the PD controller models the fact that real motors are neither perfectly tuned nor identical. The gain setters take a value per dof, and when you pass a leading `n_envs` dimension they assign a distinct controller to each environment:

```python
# Per-env, per-dof position and velocity gains. Shapes: (n_envs, n_dofs).
robot.set_dofs_kp(4000 + 1000 * torch.rand(scene.n_envs, robot.n_dofs), motors_dof_idx)
robot.set_dofs_kv(400 + 100 * torch.rand(scene.n_envs, robot.n_dofs), motors_dof_idx)
robot.set_dofs_armature(0.01 + 0.02 * torch.rand(scene.n_envs, robot.n_dofs), motors_dof_idx)
```

`set_dofs_kp` and `set_dofs_kv` set the position and velocity gains of the PD controller; `set_dofs_armature` sets the reflected motor inertia, which stabilizes stiff joints. The second positional argument is `dofs_idx_local`, the entity-local dof indices to update, matching the `motors_dof_idx` you build from joint names.

:::{warning}
Per-environment dof gains require batched dof info. The controller gains live in the model's static info fields, which are stored per environment only when the scene is built with the corresponding option. Enable it in `RigidOptions`:

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        batch_dofs_info=True,   # required for per-env kp / kv / armature
        batch_links_info=True,  # required for per-env static link info
    ),
)
```

Without `batch_dofs_info=True`, a gain tensor with an `n_envs` dimension has nowhere to go. The state-based setters above (`set_friction_ratio`, `set_mass_shift`, `set_COM_shift`) do not need these flags.
:::

## Randomizing commands and states per episode

Task randomization changes every episode, so it belongs in the reset path rather than after `build()`. The locomotion example (see {doc}`/user_guide/getting_started/policy_training/examples/locomotion`, source [`examples/locomotion/go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py)) samples a fresh velocity command whenever an environment resets or a resampling interval elapses. Its uniform-sampling helper is worth reusing:

```python
def gs_rand(lower, upper, batch_shape):
    # Uniform in [lower, upper), broadcast over the batch dimensions.
    assert lower.shape == upper.shape
    return (upper - lower) * torch.rand(size=(*batch_shape, *lower.shape), device=gs.device) + lower
```

The environment then resamples commands only for the environments passed in `envs_idx`, leaving the rest untouched:

```python
def _resample_commands(self, envs_idx):
    commands = gs_rand(*self.commands_limits, (self.num_envs,))  # shape (n_envs, num_commands)
    torch.where(envs_idx[:, None], commands, self.commands, out=self.commands)
```

The same principle applies to spawn poses and reset states: build the randomized tensor for the resetting environments, then write it with the entity setter's `envs_idx` argument so you touch only those environments. For example, `entity.set_pos(random_pos, envs_idx=envs_idx)` randomizes an object's initial position without disturbing environments that are still mid-episode.

## Methods reference

| Method | Shape | Randomizes |
|---|---|---|
| `set_friction_ratio` | `(n_envs, n_links)` | Per-link friction, as a multiplier on the base coefficient |
| `set_mass_shift` | `(n_envs, n_links)` | Per-link additive mass offset (kg) |
| `set_COM_shift` | `(n_envs, n_links, 3)` | Per-link center-of-mass offset (m) |
| `set_dofs_kp` | `(n_envs, n_dofs)` | PD position gain |
| `set_dofs_kv` | `(n_envs, n_dofs)` | PD velocity gain |
| `set_dofs_armature` | `(n_envs, n_dofs)` | Reflected motor inertia |

All six accept an optional `envs_idx` to update a subset of environments. The gain and armature setters require `batch_dofs_info=True`; the friction, mass, and COM setters do not.

## Guidelines

- **Apply physics randomization once, after `build()`.** These properties describe the body, not the episode. Resetting them every step wastes time and can destabilize the solver.
- **Apply command and state randomization at reset,** scoped with `envs_idx` so you only touch the environments that just terminated.
- **Match the leading dimension to `n_envs`.** A tensor of the wrong batch size is the most common error. Use `scene.n_envs` and the entity's `n_links` or `n_dofs` to size tensors rather than hard-coding.
- **Randomize what you cannot measure, not what you can.** Widening the distribution of a parameter you already know accurately only makes the task harder to learn. Center each range on your best estimate and widen it to cover your uncertainty.

## See also

- {doc}`/user_guide/getting_started/parallel_simulation` for how batched environments work and why per-env tensors are cheap.
- {doc}`/user_guide/getting_started/policy_training/examples/locomotion` for an end-to-end policy that uses these techniques.
- {doc}`/user_guide/getting_started/policy_training/best_practices/efficient_environment` for keeping the randomized environment fast.
