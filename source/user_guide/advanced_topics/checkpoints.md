# 💾 チェックポイント

Genesis は、学習再開やエピソードリセットのための状態保存/読込機能を提供します。

## 基本的な保存/読込

```python
import genesis as gs

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene.build()

# シミュレーション
for _ in range(100):
    scene.step()

# チェックポイント保存
scene.save_checkpoint("checkpoint.pkl")

# 新しいシーンで読込
scene2 = gs.Scene()
robot2 = scene2.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene2.build()
scene2.load_checkpoint("checkpoint.pkl")
```

## 状態オブジェクト

```python
# 現在状態を取得（メモリ上）
state = scene.get_state()

# 初期状態へリセット
scene.reset()

# 任意状態へリセット
scene.reset(state=state)
```

## RL エピソードリセット

```python
scene.build(n_envs=N)

# 初期状態をスナップショット
init_state = scene.get_state()

for episode in range(num_episodes):
    scene.reset(state=init_state)

    for step in range(episode_length):
        scene.step()
        obs, reward, done = get_observations()

        # 終了した環境のみリセット
        if done.any():
            done_envs = torch.where(done)[0].tolist()
            scene.reset(state=init_state, envs_idx=done_envs)
```

## 環境を選択したリセット

```python
scene.build(n_envs=16)

# 全環境をリセット
scene.reset()

# 特定環境のみリセット
scene.reset(envs_idx=[0, 2, 5])

# 特定環境へ任意状態を適用
scene.reset(state=init_state, envs_idx=[1, 3, 7])
```

## 状態内容

`SimState` オブジェクトには次が含まれます。

| ソルバー | 状態変数 |
|--------|-----------------|
| Rigid | `qpos`, `dofs_vel`, `links_pos`, `links_quat` |
| MPM | `pos`, `vel`, `C`, `F`, `Jp`, `active` |
| SPH | `pos`, `vel`, `active` |
| PBD | `pos`, `vel`, `free` |
| FEM | `pos`, `vel`, `active` |

## チェックポイントファイル形式

チェックポイントは pickle 化された辞書です。

```python
{
    "timestamp": time.time(),
    "step_index": scene.t,
    "arrays": {  # solver/field キーごとの Numpy 配列
        "RigidSolver.qpos": np.array(...),
        "MPMSolver.pos": np.array(...),
        ...
    }
}
```

## 転送用シリアライズ

```python
# 状態をシリアライズ可能にする（計算グラフから分離）
state = scene.get_state()
state_serializable = state.serializable()

# 安全に pickle 可能
import pickle
with open("state.pkl", "wb") as f:
    pickle.dump(state_serializable, f)
```

## 重要な注意点

- チェックポイントには互換シーン設定が必要です（同一エンティティ・同一ソルバー設定）
- 32-bit 精度では save/load 間で約 ~2e-6 の誤差が生じる場合があります
- 部分リセットには `envs_idx` を使うと効率的です
- `scene.t` はシミュレーションステップ数を保持します
