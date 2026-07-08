# Training a locomotion policy with RL

This tutorial trains a walking policy for the Unitree Go2 quadruped and rolls it out in the viewer. It is a deliberately minimal pipeline: a gym-style environment, PPO from an external RL library, and a short evaluation loop. The reward terms are simplified to get a policy walking quickly, so treat it as a starting point rather than a production locomotion stack.

The three scripts that make up the example are the source of truth for the complete code:

- [`go2_env.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_env.py): the environment: scene, control, observations, rewards, and resets.
- [`go2_train.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_train.py): hyperparameters and the training entry point.
- [`go2_eval.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/locomotion/go2_eval.py): loading a checkpoint and running the policy.

The design borrows its structure from [Legged Gym](https://github.com/leggedrobotics/legged_gym).

## Prerequisites

Training uses PPO from [rsl-rl](https://github.com/leggedrobotics/rsl_rl), an external library, and logs to TensorBoard. Install both alongside Genesis World:

```bash
pip install tensorboard "rsl-rl-lib>=5.0.0"
```

The scripts require `rsl-rl-lib>=5.0.0` and raise an `ImportError` at startup if an older version is present, because the example relies on the observation-group and `TensorDict` conventions introduced in that release.

## The environment

`Go2Env` is a standard RL environment: it owns a Genesis World {doc}`scene </api_reference/scene/scene>` built across many {doc}`environments </user_guide/getting_started/parallel_simulation>`, and it exposes `reset()` and `step(actions)`. Training runs thousands of copies of the robot in parallel on one GPU, so every buffer carries a leading `n_envs` dimension and the step logic stays vectorized on the device.

The constructor builds the scene once for all environments:

```python
self.scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=self.dt,  # 0.02 s -> 50 Hz control, matching the real robot
        substeps=2,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_self_collision=False,
        max_collision_pairs=20,  # a walking Go2 rarely exceeds this; a low cap saves memory
    ),
    ...
)
```

```python
self.scene.build(n_envs=num_envs)
```

`n_envs` is set at build time, not at construction, and everything downstream is sized to match it.

### Control

The robot is driven by a PD controller in joint-position space. The 12 leg joints are located by name, and their gains are set once after the build:

```python
self.robot.set_dofs_kp([self.env_cfg["kp"]] * self.num_actions, self.motors_dof_idx)  # kp = 20.0
self.robot.set_dofs_kv([self.env_cfg["kd"]] * self.num_actions, self.motors_dof_idx)  # kd = 0.5
```

The policy does not output torques or absolute joint angles. It outputs a residual around the robot's default standing pose, which `step` scales and adds to that pose to form a position target:

```python
target_dof_pos = exec_actions * self.env_cfg["action_scale"] + self.default_dof_pos  # action_scale = 0.25, rad
self.robot.control_dofs_position(target_dof_pos[:, self.actions_dof_idx], slice(6, 18))
```

Actuating around a default pose keeps early exploration close to a stable stance, which is what lets the policy find a gait in a few hundred iterations. The environment also feeds the *previous* step's action to the controller (`simulate_action_latency`) to reproduce the one-step (~20 ms) actuation delay a real Go2 shows, narrowing the sim-to-real gap.

### Observations

`step` reads the robot state back after `scene.step()`, converting base linear and angular velocity into the robot's own frame, then assembles the policy input:

```python
self.obs_buf = torch.concatenate(
    (
        self.base_ang_vel * self.obs_scales["ang_vel"],           # 3, base-frame angular velocity (rad/s)
        self.projected_gravity,                                   # 3, gravity direction in base frame
        self.commands * self.commands_scale,                      # 3, target lin_vel_x, lin_vel_y, ang_vel_yaw
        (self.dof_pos - self.default_dof_pos) * self.obs_scales["dof_pos"],  # 12, joint-position residual (rad)
        self.dof_vel * self.obs_scales["dof_vel"],                # 12, joint velocity (rad/s)
        self.actions,                                             # 12, previous action
    ),
    dim=-1,
)
```

The observation is a 45-dimensional vector, shape `(n_envs, 45)`. Each term is multiplied by a fixed scale so the components sit on comparable magnitudes before they reach the network. `get_observations` wraps the buffer in a `TensorDict` under the key `"policy"`, which is the format rsl-rl expects:

```python
def get_observations(self):
    return TensorDict({"policy": self.obs_buf}, batch_size=[self.num_envs])
```

The **command** is the task: a per-environment target of forward velocity, lateral velocity, and yaw rate. Commands are resampled at random within configured ranges every `resampling_time_s` and on reset, so a single policy learns to follow a distribution of velocity commands rather than one fixed gait.

### Rewards

The total reward is a weighted sum of six terms, each a method on the environment. Two terms reward the task and four regularize the motion:

| Reward term | Purpose | Scale |
|---|---|---|
| `tracking_lin_vel` | follow the commanded xy velocity | `1.0` |
| `tracking_ang_vel` | follow the commanded yaw rate | `0.2` |
| `lin_vel_z` | penalize vertical bouncing | `-1.0` |
| `base_height` | hold the base near its target height | `-50.0` |
| `action_rate` | penalize jerky action changes | `-0.005` |
| `similar_to_default` | stay near the default joint pose | `-0.1` |

The two tracking terms use an exponential of the squared error, which rewards getting close without overweighting near-perfect tracking:

```python
def _reward_tracking_lin_vel(self):
    # Tracking of linear velocity commands (xy axes)
    lin_vel_error = torch.sum(torch.square(self.commands[:, :2] - self.base_lin_vel[:, :2]), dim=1)
    return torch.exp(-lin_vel_error / self.reward_cfg["tracking_sigma"])
```

Each raw term is multiplied by its scale and by `dt`, so the weights read as per-second rates and stay independent of the control frequency. All reward configuration lives in `get_cfgs` in `go2_train.py`; tuning behavior means editing those scales, not the environment.

### Resets

`step` marks an environment for reset when its episode reaches `episode_length_s`, when the base roll or pitch exceeds 10 degrees (the robot has fallen), or when the physics solver flags a numerical error. Flagged environments are reset in place to the initial pose without interrupting the others, and a fresh command is drawn for each.

## Training

With the environment defined, `go2_train.py` hands it to rsl-rl's `OnPolicyRunner`, which trains a PPO policy. The actor and critic are both three-layer MLPs (`[512, 256, 128]`, ELU); the full hyperparameter set is in `get_train_cfg`. Genesis World is initialized on the GPU with `performance_mode=True`, which bakes static tensor shapes into the compiled kernels for faster stepping at the cost of recompiling when the scene changes, a worthwhile trade for a long training run:

```python
gs.init(backend=gs.gpu, precision="32", logging_level="warning", seed=args.seed, performance_mode=True)
```

Start training from the repository root:

```bash
python examples/locomotion/go2_train.py
```

By default this runs 4096 environments in parallel for 101 iterations under the experiment name `go2-walking`, saving checkpoints and a `cfgs.pkl` (the exact configs used) into `logs/go2-walking/`. Override any of these with `-B/--num_envs`, `--max_iterations`, or `-e/--exp_name`.

Monitor progress with TensorBoard:

```bash
tensorboard --logdir logs
```

```{figure} ../../../_static/images/locomotio_curve.png
:alt: TensorBoard reward curves rising over training iterations for the Go2 walking policy
```

## Evaluation

`go2_eval.py` reloads the saved configs, rebuilds the environment with a single visualized instance, restores a checkpoint, and steps the policy in a loop:

```python
runner.load(os.path.join(log_dir, f"model_{args.ckpt}.pt"))
policy = runner.get_inference_policy(device=gs.device)

obs_dict = env.reset()
with torch.no_grad():
    while True:
        actions = policy(obs_dict)
        obs_dict, rews, dones, infos = env.step(actions)
```

Evaluation initializes Genesis World on the CPU (`gs.init(backend=gs.cpu)`), which is sufficient for a single environment with the viewer open. Run it with the experiment name and checkpoint to load:

```bash
python examples/locomotion/go2_eval.py -e go2-walking --ckpt 100
```

```{video} ../../../_static/videos/locomotion_eval.mp4
:width: 100%
```

The trained policy is a standard joint-position controller and can be deployed to a physical Go2.

```{video} ../../../_static/videos/locomotion_real.mp4
:width: 100%
```

## Variations

`go2_backflip.py` reuses the same `Go2Env` machinery for a dynamic backflip. It subclasses the environment to add a phase-based observation and loads a pre-trained TorchScript policy, showing how far the base environment stretches beyond flat walking:

```bash
python examples/locomotion/go2_backflip.py -e single
```

## See also

- {doc}`Best practices <../best_practices/index>` for keeping the step loop on the GPU and randomizing physics across environments.
- {doc}`hover_env` for the same pipeline applied to a quadcopter, and {doc}`manipulation` for a two-stage manipulation policy.
