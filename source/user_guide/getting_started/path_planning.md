# 🗺️ 経路計画

Genesis は、衝突回避ロボット経路のための RRT ベースのモーションプランニングを提供します。

## 基本的な使い方

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
obstacle = scene.add_entity(gs.morphs.Box(pos=(0.5, 0, 0.3), size=(0.1, 0.3, 0.3), fixed=True))
scene.build()

# 目標姿勢を定義
goal_qpos = robot.inverse_kinematics(
    link=robot.get_link("hand"),
    pos=np.array([0.6, 0.0, 0.3]),
)

# 衝突のない経路を計画
path = robot.plan_path(qpos_goal=goal_qpos, num_waypoints=200)

# 経路を実行
for waypoint in path:
    robot.control_dofs_position(waypoint)
    scene.step()
```

## パラメータ

```python
robot.plan_path(
    qpos_goal,                  # 目標姿勢（必須）
    qpos_start=None,            # 開始姿勢（デフォルト: 現在値）
    planner="RRTConnect",       # "RRT" または "RRTConnect"
    num_waypoints=300,          # 出力経路長
    resolution=0.05,            # 計画分解能
    smooth_path=True,           # 経路平滑化を適用
    max_nodes=4000,             # 木の最大ノード数
    timeout=None,               # 各試行のタイムアウト（秒）
    max_retry=1,                # リトライ回数
    ignore_collision=False,     # 衝突判定をスキップ
)
```

## プランナー種別

- **RRTConnect**（デフォルト）: 双方向探索でより効率的
- **RRT**: 単一木探索でよりシンプル

## 物体を把持した状態での計画

物体を保持したまま計画します。

```python
path = robot.plan_path(
    qpos_goal=target_qpos,
    ee_link_name="hand",
    with_entity=cube,
)
```

## 計画成功の確認

```python
path, is_valid = robot.plan_path(
    qpos_goal=target_qpos,
    return_valid_mask=True,
)

if is_valid:
    print("Planning succeeded!")
```

## マルチ環境での計画

```python
scene.build(n_envs=16)

# 全環境で計画
path = robot.plan_path(qpos_goal=target_qpos)
print(path.shape)  # (num_waypoints, 16, n_dofs)

# 特定環境のみ計画
path, valid = robot.plan_path(
    qpos_goal=target_qpos,
    envs_idx=[0, 5, 10],
    return_valid_mask=True,
)
```

## パフォーマンスのヒント

- `resolution` を大きくすると高速化（ただし品質は低下）
- `resolution` を小さくすると経路が滑らかになる
- 信頼性向上には `timeout` と `max_retry` を使う
- 一般に `RRTConnect` は `RRT` より高速
