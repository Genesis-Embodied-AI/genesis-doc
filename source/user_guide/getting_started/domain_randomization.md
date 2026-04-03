# 🎲 ドメインランダム化

ロバストな RL 学習のために、物理特性と見た目の特性をランダム化します。

## 物理パラメータのランダム化

`scene.build()` の後に適用します。

```python
import genesis as gs
import torch

scene.build(n_envs=64)

# 摩擦ランダム化
robot.set_friction_ratio(
    friction_ratio=0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# 質量ランダム化
robot.set_mass_shift(
    mass_shift=-0.5 + torch.rand(scene.n_envs, robot.n_links),
    links_idx_local=range(robot.n_links),
)

# 重心ランダム化
robot.set_COM_shift(
    com_shift=-0.05 + 0.1 * torch.rand(scene.n_envs, robot.n_links, 3),
    links_idx_local=range(robot.n_links),
)
```

## 制御パラメータのランダム化

```python
import numpy as np

# 環境ごとの剛性 (Kp)
kp_values = 4000 + 1000 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kp(kp_values, motors_dof)

# 環境ごとの減衰 (Kv)
kv_values = 400 + 100 * np.random.rand(scene.n_envs, robot.n_dofs)
robot.set_dofs_kv(kv_values, motors_dof)
```

## 物体位置のランダム化（エピソードごと）

```python
def reset_idx(self, envs_idx):
    num_reset = len(envs_idx)

    # 物体位置をランダム化
    random_x = torch.rand(num_reset, device=gs.device) * 0.4 + 0.2
    random_y = (torch.rand(num_reset, device=gs.device) - 0.5) * 0.5
    random_z = torch.ones(num_reset, device=gs.device) * 0.025
    random_pos = torch.stack([random_x, random_y, random_z], dim=-1)

    self.object.set_pos(random_pos, envs_idx=envs_idx)
```

## コマンドのランダム化

```python
def gs_rand(lower, upper, shape):
    """[lower, upper] の一様乱数"""
    return (upper - lower) * torch.rand(shape, device=gs.device) + lower

# 速度コマンドをランダム化
commands = gs_rand(
    lower=torch.tensor([-1.0, -0.5, -0.5]),
    upper=torch.tensor([1.0, 0.5, 0.5]),
    shape=(self.num_envs, 3),
)
```

## 利用可能なメソッド

| メソッド | 形状 | 説明 |
|--------|-------|-------------|
| `set_friction_ratio` | (n_envs, n_links) | 摩擦スケーリング |
| `set_mass_shift` | (n_envs, n_links) | 質量オフセット |
| `set_COM_shift` | (n_envs, n_links, 3) | 重心オフセット |
| `set_dofs_kp` | (n_envs, n_dofs) | 位置ゲイン |
| `set_dofs_kv` | (n_envs, n_dofs) | 速度ゲイン |
| `set_dofs_armature` | (n_envs, n_dofs) | モーター慣性 |

## 必要なオプション

物理ランダム化のためにバッチ設定を有効にします。

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        batch_dofs_info=True,
        batch_links_info=True,
    ),
)
```

## ベストプラクティス

1. 物理 DR は `scene.build()` 後に一度だけ適用する
2. 位置・コマンド DR は各エピソードのリセット時に適用する
3. 部分的なランダム化には `envs_idx` パラメータを使う
4. テンソル形状を `(n_envs, ...)` に一致させる
