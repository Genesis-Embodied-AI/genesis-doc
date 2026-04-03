# ⚡ IPC カップラー

Genesis は、高忠実度な変形体-剛体相互作用のために Incremental Potential Contact（IPC）カップリングを提供します。

## 要件

`libuipc` ライブラリが必要です（https://github.com/spiriMirror/libuipc からビルド）。

## 基本設定

```python
import genesis as gs

dt = 0.01
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=dt, gravity=(0.0, 0.0, -9.8)),
    coupler_options=gs.options.IPCCouplerOptions(
        dt=dt,
        gravity=(0.0, 0.0, -9.8),
    ),
)
```

## 主要パラメータ

| パラメータ | 既定値 | 説明 |
|-----------|---------|-------------|
| `dt` | 0.001 | IPC シミュレーションのタイムステップ |
| `contact_d_hat` | 0.001 | 接触バリア距離 |
| `contact_friction_mu` | 0.5 | 摩擦係数 |
| `ipc_constraint_strength` | (100, 100) | （並進, 回転）カップリング強度 |
| `two_way_coupling` | True | IPC 力を剛体へ反映 |
| `IPC_self_contact` | False | 剛体-剛体自己衝突を有効化 |
| `enable_ipc_gui` | False | Polyscope 可視化 |

## クロスシミュレーション

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=2e-3,
        contact_d_hat=0.01,
        contact_friction_mu=0.3,
        enable_ipc_gui=True,
    ),
)

cloth = scene.add_entity(
    morph=gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.FEM.Cloth(
        E=10e5,
        nu=0.499,
        rho=200,
        thickness=0.001,
        bending_stiffness=50.0,
    ),
)
```

## ロボット把持

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=1e-2,
        ipc_constraint_strength=(100, 100),
        contact_friction_mu=0.8,
        two_way_coupling=True,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))

# IPC に参加するリンクをフィルタ
scene.sim.coupler.set_ipc_link_filter(
    entity=franka,
    link_names=["left_finger", "right_finger"],
)

cube = scene.add_entity(
    morph=gs.morphs.Box(),
    material=gs.materials.FEM.Elastic(E=5e3, nu=0.45, rho=1000),
)
```

## IPC を使うべき場面

**IPC が適するケース:**
- 衝突を含むクロス/布シミュレーション
- FEM 物体と剛体の相互作用
- 高品質な把持シミュレーション
- 安定した拘束ベース接触解決

**LegacyCoupler が適するケース:**
- 単純な rigid-MPM, rigid-SPH 相互作用
- 計算負荷を抑えたい場合
- IPC ライブラリが利用できない場合

## 接触処理

| 相互作用 | IPC の挙動 |
|-------------|--------------|
| FEM-FEM | 常に有効 |
| FEM-Rigid | 常に有効 |
| Rigid-Rigid | `IPC_self_contact` オプション |
| Cloth-Cloth | 常に有効（自己衝突） |

## パフォーマンスのヒント

- `contact_d_hat` はメッシュ分解能に合わせて設定（通常 0.5-2mm）
- `ipc_constraint_strength` を上げると剛性は増えるが不安定化する場合がある
- 地面衝突の二重計算を避けるには `disable_genesis_ground_contact=True` を使う
