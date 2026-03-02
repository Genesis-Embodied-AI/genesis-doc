# 🔗 ハイブリッドエンティティ

HybridEntity は、剛体と軟体の物理を組み合わせ、剛体スケルトンを持つ変形ロボットをシミュレーションします。

## 概要

Hybrid Entity は次を結合します。
- **Rigid コンポーネント**: スケルトン/構造（URDF 由来）
- **Soft コンポーネント**: 変形スキン（MPM ベース）

利用例: ソフトグリッパー、変形ロボット、コンプライアントマニピュレータ。

## ハイブリッドエンティティの作成

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=3e-3, substeps=10),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(0, 0, -0.2),
        upper_bound=(1, 1, 1),
    ),
)

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="robot.urdf",
        pos=(0.5, 0.5, 0.3),
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.05,
        damping=1000.0,
    ),
)

scene.build()
```

## ハイブリッドマテリアルのオプション

```python
gs.materials.Hybrid(
    material_rigid=gs.materials.Rigid(),     # 剛体マテリアル
    material_soft=gs.materials.MPM.Muscle(), # 軟体マテリアル（MPM のみ）
    thickness=0.05,                          # 軟体スキン厚み
    damping=1000.0,                          # 速度減衰
    soft_dv_coef=0.01,                       # Rigid→Soft 速度伝達
)
```

## 制御

制御は剛体スケルトンの DOF を使います。

```python
import numpy as np

for step in range(1000):
    # 正弦波の関節制御
    target_vel = [np.sin(step * 0.01)] * robot.n_dofs
    robot.control_dofs_velocity(target_vel)
    scene.step()
```

## コンポーネントへのアクセス

```python
robot.part_rigid   # RigidEntity（スケルトン）
robot.part_soft    # MPMEntity（スキン）
robot.n_dofs       # DOF 数

# 状態アクセス
robot.get_dofs_position()
robot.get_dofs_velocity()
```

## 例: ソフトグリッパー

```python
gripper = scene.add_entity(
    morph=gs.morphs.URDF(file="gripper.urdf", fixed=True),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.02,
        damping=100.0,
    ),
)

# 把持対象を追加
ball = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.5, 0.5, 0.1), radius=0.05),
)

scene.build()

# グリッパーを閉じる
for step in range(500):
    gripper.control_dofs_position([0.5] * gripper.n_dofs)
    scene.step()
```

## メッシュから作成（自動スケルトン化）

任意メッシュから Hybrid Entity を作成できます。

```python
creature = scene.add_entity(
    morph=gs.morphs.Mesh(file="creature.obj", scale=0.1),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(),
        material_soft=gs.materials.MPM.Muscle(E=1e4),
    ),
)
```

Genesis は自動的に以下を行います。
1. スケルトン化によりメッシュから骨格を抽出
2. 骨格から剛体を作成
3. 軟体粒子を骨格リンクへ対応付け

## 注意点

- 軟体マテリアルは MPM ベース（`gs.materials.MPM.*`）である必要があります
- `damping` を大きくすると振動が減少します
- 適切な境界を設定した `mpm_options` が必要です
