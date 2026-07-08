# Training a drone hover policy with RL

This tutorial trains a quadrotor to hover at randomly placed target points using reinforcement learning (RL). It follows the standard three-file layout for an RL example in Genesis World: an environment that wraps the simulation as a gym-style task, a training script, and an evaluation script. The policy you obtain is small enough to run on a real Crazyflie.

The reward design follows [Champion-level drone racing using deep reinforcement learning (Nature 2023)](https://www.nature.com/articles/s41586-023-06419-4.pdf). This is a minimal starting point, not a production pipeline: the reward terms are deliberately simple, and the default batch size does not push Genesis World's parallel throughput.

The three files are the source of truth for the complete code:

- [`examples/drone/hover_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/hover_env.py) defines the `HoverEnv` task.
- [`examples/drone/hover_train.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/hover_train.py) configures PPO and runs training.
- [`examples/drone/hover_eval.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/hover_eval.py) loads a checkpoint and rolls out the policy.

The drone is actuated purely through its four propeller speeds. If you have not seen how RPM becomes thrust and attitude, read {doc}`/user_guide/getting_started/drone_entity` first; this page assumes that mapping.

## The task

Each episode places a target point in front of the drone and rewards it for flying to that point and holding position. When the drone gets within `at_target_threshold` (0.1 m) of the target, a fresh target is resampled, so a single episode chains many reach-and-hold maneuvers. An episode lasts up to `episode_length_s` (15 s) and terminates early on a crash.

The task is defined by three things the environment must specify for any RL problem: an observation the policy sees, an action it produces, and a reward that scores the outcome.

## The environment

`HoverEnv` is a plain Python class, not a subclass of a gym base class. It exposes the methods an on-policy RL runner expects: `reset()`, `step(actions)`, and `get_observations()`. All of its state lives in batched tensors of shape `(n_envs, ...)`, so a single instance drives thousands of drones in parallel on the GPU.

### Scene and drone

The constructor builds a scene at a 100 Hz control rate and adds a ground plane, an optional target marker, and the Crazyflie drone:

```python
self.dt = 0.01  # 100 Hz control loop
self.scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=self.dt, substeps=2),
    rigid_options=gs.options.RigidOptions(
        dt=self.dt,
        constraint_solver=gs.constraint_solver.Newton,
        enable_collision=True,
        enable_joint_limit=True,
    ),
    show_viewer=show_viewer,
)
self.scene.add_entity(gs.morphs.Plane())
self.drone = self.scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf"))
self.scene.build(n_envs=num_envs)
```

`build(n_envs=num_envs)` is what allocates the batched simulation. During training this is 8192 environments; during evaluation it is 1.

### Actions

The policy outputs four numbers, one per propeller, clipped to `[-1, 1]`. The environment maps them to propeller RPM as a fraction of the hover RPM, the speed at which total thrust balances gravity:

```python
self.actions = torch.clip(actions, -self.env_cfg["clip_actions"], self.env_cfg["clip_actions"])
# 14468 rpm is the hover point; actions scale each propeller to [0.2, 1.8] x hover
self.drone.set_propellers_rpm((1 + self.actions * 0.8) * 14468.429183500699)
self.scene.step()
```

Learning a fraction of hover RPM rather than an absolute RPM keeps the action range small and centered, which stabilizes early training. See {py:meth}`~genesis.engine.entities.drone_entity.DroneEntity.set_propellers_rpm` for the RPM-to-force conversion.

### Observations

After each step the environment reads the drone's state and assembles the observation. It is a length-17 vector per environment, with each block scaled into roughly `[-1, 1]` so no single quantity dominates the policy input:

```python
self.obs_buf = torch.cat(
    [
        torch.clip(self.rel_pos * self.obs_scales["rel_pos"], -1, 1),  # target minus drone position (3,)
        self.base_quat,                                                # attitude, (w, x, y, z) (4,)
        torch.clip(self.base_lin_vel * self.obs_scales["lin_vel"], -1, 1),  # body-frame linear velocity (3,)
        torch.clip(self.base_ang_vel * self.obs_scales["ang_vel"], -1, 1),  # body-frame angular velocity (3,)
        self.last_actions,                                             # previous action (4,)
    ],
    axis=-1,
)  # shape (n_envs, 17)
```

Linear and angular velocities are expressed in the drone's body frame (rotated by the inverse of the base quaternion), which makes the policy invariant to the drone's heading. Position error `rel_pos` is `target - drone_position` in world coordinates. Attitude is a quaternion in `(w, x, y, z)` scalar-first order.

### Rewards

Five terms are summed each step, each scaled by `dt` and a weight from `reward_cfg`. The weights (positive rewards, negative penalties) live in `hover_train.py`:

- **target:** rewards closing the distance to the target. It is potential-based: the reduction in squared distance from the previous step, so progress toward the target scores positively regardless of absolute distance.
- **smooth:** penalizes large step-to-step changes in action, which suppresses jitter and narrows the sim-to-real gap.
- **yaw:** rewards keeping heading near zero, using `exp(yaw_lambda * |yaw|)`.
- **angular:** penalizes body angular velocity, discouraging spin.
- **crash:** a fixed penalty applied on any terminating condition below.

### Termination and reset

An environment terminates and resets when it times out or crashes. The crash conditions guard against unrecoverable states:

- roll or pitch exceeds its threshold (180 degrees),
- the drone drifts more than 3.0 m in x or y, or 2.0 m in z, from the target,
- the drone descends below 0.1 m (into the ground).

`reset_idx` re-initializes only the terminated environments in place, so the batch never stalls waiting for the slowest episode. Resets re-sample a new target and zero the state buffers.

## Training

Training uses PPO from [`rsl-rl`](https://github.com/leggedrobotics/rsl_rl). Install the dependencies:

```bash
pip install --upgrade pip
pip install tensorboard "rsl-rl-lib>=5.0.0"
```

`hover_train.py` initializes Genesis World for the GPU in performance mode, constructs `HoverEnv`, wraps it in an `OnPolicyRunner`, and calls `learn`:

```python
gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=args.seed, performance_mode=True)
env = HoverEnv(num_envs=args.num_envs, env_cfg=env_cfg, obs_cfg=obs_cfg,
               reward_cfg=reward_cfg, command_cfg=command_cfg, show_viewer=args.vis)
runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
runner.learn(num_learning_iterations=args.max_iterations, init_at_random_ep_len=True)
```

`performance_mode=True` bakes the tensor shapes into the compiled kernels for faster stepping, at the cost of a slower first build. It is the right choice for a long training run and the wrong one for interactive iteration.

The actor and critic are both two-layer MLPs (`[128, 128]`, `tanh`), configured in `get_train_cfg`. Start training with:

```bash
python hover_train.py -e drone-hovering -B 8192 --max_iterations 301
```

- **`-e drone-hovering`:** experiment name; checkpoints and configs are written to `logs/drone-hovering/`.
- **`-B 8192`:** number of parallel environments.
- **`--max_iterations 301`:** number of PPO iterations.
- **`-v`:** optional, opens the viewer to watch training.

Monitor progress with TensorBoard:

```bash
tensorboard --logdir logs
```

```{figure} ../../../../_static/images/hover_curve.png
:alt: TensorBoard reward curve rising and plateauing over training iterations
```

With `-v`, the viewer shows a handful of environments training in parallel:

```{figure} ../../../../_static/images/training.gif
:alt: Several Crazyflie drones learning to fly toward target markers in the viewer
```

## Evaluation

`hover_eval.py` reloads the saved configs, rebuilds the environment with a single drone and the viewer open, and rolls out the trained policy deterministically:

```bash
python hover_eval.py -e drone-hovering --ckpt 300 --record
```

- **`--ckpt 300`:** loads `logs/drone-hovering/model_300.pt`.
- **`--record`:** attaches a camera and saves the rollout to `video.mp4`.

If evaluation is slow or unstable, drop `--record` to disable rendering.

<video controls width="100%">
  <source src="../../../../_static/videos/hover_env.mp4" type="video/mp4">
  A trained Crazyflie drone hovering at randomly sampled target points.
</video>

## See also

- {doc}`/user_guide/getting_started/drone_entity` for how propeller RPM produces thrust, attitude, and yaw.
- {doc}`locomotion` and {doc}`manipulation` for the same environment/train/eval structure applied to other tasks.
