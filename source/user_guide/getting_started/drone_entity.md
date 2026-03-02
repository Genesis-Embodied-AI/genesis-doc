# 🚁 ドローンエンティティ

Genesis は、プロペラ物理とモーター制御を備えた専用ドローンシミュレーションを提供します。

## ドローンの作成

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, gravity=(0, 0, -9.81)),
)

scene.add_entity(gs.morphs.Plane())

drone = scene.add_entity(
    morph=gs.morphs.Drone(
        file="urdf/drones/cf2x.urdf",
        model="CF2X",
        pos=(0.0, 0.0, 0.5),
    ),
)

scene.build()
```

## ドローン Morph オプション

```python
gs.morphs.Drone(
    file="urdf/drones/cf2x.urdf",  # URDF ファイルパス
    model="CF2X",                   # モデル: "CF2X", "CF2P", または "RACE"
    pos=(0.0, 0.0, 0.5),            # 初期位置
    euler=(0.0, 0.0, 0.0),          # 初期姿勢（度）
    propellers_link_name=('prop0_link', 'prop1_link', 'prop2_link', 'prop3_link'),
    propellers_spin=(-1, 1, -1, 1), # 回転方向: 1=CCW, -1=CW
)
```

## モーター制御

RPM（1分あたり回転数）でプロペラを制御します。

```python
hover_rpm = 14475.8  # CF2X のホバリング目安 RPM
max_rpm = 25000.0

for step in range(1000):
    # 各プロペラの RPM [front-left, front-right, back-left, back-right]
    rpms = np.array([hover_rpm, hover_rpm, hover_rpm, hover_rpm])

    # 差動推力を加えて運動を作る
    rpms[0] += 100  # front-left を増加
    rpms[3] += 100  # back-right を増加
    rpms = np.clip(rpms, 0, max_rpm)

    drone.set_propellels_rpm(rpms)  # 1 ステップにつき 1 回だけ呼ぶ
    scene.step()
```

**重要:** `set_propellels_rpm()` はシミュレーション 1 ステップにつき必ず 1 回だけ呼び出してください。

## 物理モデル

- **推力:** `F = KF × RPM²`（プロペラごとの鉛直力）
- **トルク:** `τ = KM × RPM² × spin_direction`（ヨー方向モーメント）
- **制御:**
  - プロペラ間の差動推力 → 並進
  - ペア間の差動モーメント → 回転

## マルチ環境

```python
scene.build(n_envs=32)

# 制御入力形状: (n_envs, n_propellers)
rpms = np.tile([hover_rpm] * 4, (32, 1))
drone.set_propellels_rpm(rpms)
```

## 利用可能なモデル

| モデル | ファイル | 説明 |
|-------|------|-------------|
| CF2X | `urdf/drones/cf2x.urdf` | Crazyflie 2.0 X 構成 |
| CF2P | `urdf/drones/cf2p.urdf` | Crazyflie 2.0 Plus 構成 |
| RACE | `urdf/drones/racer.urdf` | レーシングドローン |

## 例: ホバリング制御

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
drone = scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0, 0, 1)))
scene.build()

target_height = 1.0
kp = 5000.0

for _ in range(500):
    pos = drone.get_pos()[0]
    error = target_height - pos[2].item()

    base_rpm = 14475.8
    correction = kp * error
    rpms = np.clip([base_rpm + correction] * 4, 0, 25000)

    drone.set_propellels_rpm(rpms)
    scene.step()
```
