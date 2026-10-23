# Domain randomization

A policy trained in a single, fixed simulation learns the quirks of that exact simulation. On real hardware, where friction, link masses, and actuator gains differ from your model and drift over time, that policy fails. **Domain randomization** closes the gap: you sample a different set of physical and task parameters for each parallel environment, so the policy sees a distribution of dynamics during training and learns behavior that does not depend on any single set of values.

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

# Scale each link's mass by a per-env factor in [0.75, 1.25).
robot.set_links_mass(
    mass=robot.get_links_mass() * (0.75 + 0.5 * torch.rand(scene.n_envs, robot.n_links, device=gs.device)),
)

# Shift each link's center of mass by up to 5 cm on each axis.
robot.set_links_COM(
    com=robot.get_links_COM() + (-0.05 + 0.1 * torch.rand(scene.n_envs, robot.n_links, 3, device=gs.device)),
)
```

The three methods differ in what they modify:

- **`set_friction_ratio`:** multiplies each geom's base friction coefficient by the supplied factor, shape `(n_envs, n_links)`. It scales rather than replaces, so a ratio of `1.0` leaves the model's friction unchanged. To set an absolute coefficient for the whole entity instead, use `set_friction(friction)`, which takes a single float and requires it in the range `[1e-2, 5.0]` for stability.
- **`set_links_mass`:** sets the mass of each link in kg, shape `(n_envs, n_links)`, and leaves its inertia as authored. It takes the mass itself, which is why the example reads the model's masses back with `get_links_mass` and writes scaled ones.
- **`set_links_COM`:** sets the center of mass of each link in meters, shape `(n_envs, n_links, 3)`, as an offset in the link's local frame. It takes the position itself too, so the example shifts what `get_links_COM` returns.

`set_friction_ratio` writes per-environment state, so it works in any scene. A per-environment mass or center of mass describes the model itself, which Genesis World stores per environment only when the scene is built with `batch_links_info=True` (see the warning below). A single value shared by every environment needs no flag. Pass `envs_idx` to any of them to restrict the update to a subset of environments.

## Randomizing actuator gains

Randomizing the PD controller models the fact that real motors are neither perfectly tuned nor identical. The gain setters take a value per dof, and when you pass a leading `n_envs` dimension they assign a distinct controller to each environment:

```python
# Per-env, per-dof position and velocity gains. Shapes: (n_envs, len(motors_dof_idx)).
robot.set_dofs_kp(4000 + 1000 * torch.rand(scene.n_envs, len(motors_dof_idx)), motors_dof_idx)
robot.set_dofs_kv(400 + 100 * torch.rand(scene.n_envs, len(motors_dof_idx)), motors_dof_idx)
robot.set_dofs_armature(0.01 + 0.02 * torch.rand(scene.n_envs, len(motors_dof_idx)), motors_dof_idx)
```

`set_dofs_kp` and `set_dofs_kv` set the position and velocity gains of the PD controller; `set_dofs_armature` sets the reflected motor inertia, which stabilizes stiff joints. The second positional argument is `dofs_idx_local`, the entity-local dof indices to update, matching the `motors_dof_idx` you build from joint names.

:::{warning}
Per-environment dof gains require batched dof info, and per-environment link masses, centers of mass and inertias require batched link info. Both live in the model's static info fields, which are stored per environment only when the scene is built with the corresponding option. Enable it in {py:class}`RigidOptions <genesis.options.solvers.RigidOptions>`:

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        batch_dofs_info=True,   # required for per-env kp / kv / armature
        batch_links_info=True,  # required for per-env static link info
    ),
)
```

Without `batch_dofs_info=True`, a gain tensor with an `n_envs` dimension has nowhere to go, and the same holds for a per-environment mass, center of mass or inertia without `batch_links_info=True`. `set_friction_ratio` needs neither flag.
:::

## Randomizing commands and states per episode

Task randomization changes every episode, so it belongs in the reset path rather than after `build()`. The locomotion example (see {doc}`/user_guide/policy_training/examples/locomotion`, source [`examples/locomotion/go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py)) samples a fresh velocity command whenever an environment resets or a resampling interval elapses. Its uniform-sampling helper is worth reusing:

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
| `set_links_mass` | `(n_envs, n_links)` | Per-link mass (kg) |
| `set_links_COM` | `(n_envs, n_links, 3)` | Per-link center of mass (m), in the link frame |
| `set_links_inertia` | `(n_envs, n_links, 3, 3)` | Per-link inertia matrix, in the inertial frame |
| `set_dofs_kp` | `(n_envs, len(dofs_idx_local))` | PD position gain |
| `set_dofs_kv` | `(n_envs, len(dofs_idx_local))` | PD velocity gain |
| `set_dofs_armature` | `(n_envs, len(dofs_idx_local))` | Reflected motor inertia |

All seven accept an optional `envs_idx` to update a subset of environments. The gain and armature setters require `batch_dofs_info=True`, the mass, center of mass and inertia setters require `batch_links_info=True`, and `set_friction_ratio` requires neither.

## Guidelines

- **Apply physics randomization once, after `build()`.** These properties describe the body, not the episode. Resetting them every step wastes time and can destabilize the solver.
- **Apply command and state randomization at reset,** scoped with `envs_idx` so you only touch the environments that just terminated.
- **Match the leading dimension to `n_envs`.** A tensor of the wrong batch size is the most common error. Use `scene.n_envs` and the entity's `n_links` or `n_dofs` to size tensors rather than hard-coding.
- **Randomize what you cannot measure, not what you can.** Widening the distribution of a parameter you already know accurately only makes the task harder to learn. Center each range on your best estimate and widen it to cover your uncertainty.

## See also

- {doc}`/user_guide/getting_started/parallel_simulation`: how batched environments work and why per-env tensors are cheap.
- {doc}`/user_guide/policy_training/examples/locomotion`: an end-to-end policy that uses these techniques.
- {doc}`/user_guide/policy_training/best_practices/efficient_environment`: keeping the randomized environment fast.
