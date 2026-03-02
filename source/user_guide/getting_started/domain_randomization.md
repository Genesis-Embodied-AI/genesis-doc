# 🎲 Domain Randomization

Randomize physics and visual properties for robust RL training.

## Physics Randomization

Apply after `scene.build()`:

```python
import genesis as gs
import torch

scene.build(n_envs=64)

# Friction randomization
robot.set_friction_ratio(
    friction_ratio=0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# Mass randomization
robot.set_mass_shift(
    mass_shift=-0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# Center of mass randomization
robot.set_COM_shift(
    com_shift=-0.05 + 0.1 * torch.rand(scene.n_envs, robot.n_links, 3),
    links_idx_local=range(robot.n_links),
)
```

## Control Parameter Randomization

```python
import numpy as np

# Per-environment stiffness (Kp)
kp_values = 4000 + 1000 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kp(kp_values, motors_dof)

# Per-environment damping (Kv)
kv_values = 400 + 100 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kv(kv_values, motors_dof)
```

## Object Position Randomization (Per-Episode)

```python
def reset_idx(self, envs_idx):
    num_reset = len(envs_idx)

    # Random object position
    random_x = torch.rand(num_reset, device=gs.device) * 0.4 + 0.2
    random_y = (torch.rand(num_reset, device=gs.device) - 0.5) * 0.5
    random_z = torch.ones(num_reset, device=gs.device) * 0.025
    random_pos = torch.stack([random_x, random_y, random_z], dim=-1)

    self.object.set_pos(random_pos, envs_idx=envs_idx)
```

## Command Randomization

```python
def gs_rand(lower, upper, shape):
    """Uniform random in [lower, upper]"""
    return (upper - lower) * torch.rand(shape, device=gs.device) + lower

# Randomize velocity commands
commands = gs_rand(
    lower=torch.tensor([-1.0, -0.5, -0.5]),
    upper=torch.tensor([1.0, 0.5, 0.5]),
    shape=(self.num_envs, 3),
)
```

## Available Methods

| Method | Shape | Description |
|--------|-------|-------------|
| `set_friction_ratio` | (n_envs, n_links) | Friction scaling |
| `set_mass_shift` | (n_envs, n_links) | Mass offset |
| `set_COM_shift` | (n_envs, n_links, 3) | COM offset |
| `set_dofs_kp` | (n_envs, n_dofs) | Position gain |
| `set_dofs_kv` | (n_envs, n_dofs) | Velocity gain |
| `set_dofs_armature` | (n_envs, n_dofs) | Motor inertia |

## Required Options

Enable batching for physics randomization:

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        batch_dofs_info=True,
        batch_links_info=True,
    ),
)
```

## Best Practices

1. Apply physics DR once after `scene.build()`
2. Apply position/command DR at each episode reset
3. Use `envs_idx` parameter for selective randomization
4. Ensure tensor shapes match `(n_envs, ...)`
