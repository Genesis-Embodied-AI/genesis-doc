# 🔒 制約

Genesis は、吸着把持のようなマニピュレーションタスク向けにランタイム制約をサポートしています。

## Weld（溶接）制約

Weld 制約は、2つのリンクを剛体的に固定します（6 DOF 制約）。

### Weld 制約を追加する

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
franka = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
cube = scene.add_entity(gs.morphs.Box(pos=(0.65, 0, 0.02), size=(0.04, 0.04, 0.04)))
scene.build()

# リンクハンドルを取得
rigid = scene.sim.rigid_solver
end_effector = franka.get_link("hand")
cube_link = cube.base_link

# 制約用配列を作成
link_cube = np.array([cube_link.idx], dtype=gs.np_int)
link_franka = np.array([end_effector.idx], dtype=gs.np_int)

# Weld 制約を追加（吸着オン）
rigid.add_weld_constraint(link_cube, link_franka)
```

### Weld 制約を削除する

```python
# 物体を離す
rigid.delete_weld_constraint(link_cube, link_franka)
```

## 吸着カップの例

```python
# 物体位置へ移動
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(50):
    scene.step()

# 取り付け（吸着オン）
rigid.add_weld_constraint(link_cube, link_franka)

# 持ち上げ
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.65, 0.0, 0.28]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# 配置
qpos = franka.inverse_kinematics(link=end_effector, pos=np.array([0.4, 0.2, 0.13]))
franka.control_dofs_position(qpos[:-2], motors_dof)
for _ in range(100):
    scene.step()

# 解放（吸着オフ）
rigid.delete_weld_constraint(link_cube, link_franka)
```

## マルチ環境での制約

```python
scene.build(n_envs=4)

# 特定環境に制約を追加
rigid.add_weld_constraint(link_cube, link_franka, envs_idx=(0, 1, 2))

# 一部環境から削除
rigid.delete_weld_constraint(link_cube, link_franka, envs_idx=(0, 1))
```

## Connect（接続）制約

Connect 制約は、位置のみを一致させる制約（3 DOF）で、相対回転は許容します。

```xml
<!-- MJCF/URDF 内 -->
<equality>
    <connect name="ball_joint" body1="link_1" body2="link_2" anchor="0 0 1" />
</equality>
```

## 有効な制約の取得

```python
constraints = rigid.get_weld_constraints()
print(constraints)  # 有効な制約ペア
```

## 制約の性質

- **Weld**: 6-DOF 完全拘束（並進 + 回転）
- **Connect**: 3-DOF 拘束（並進のみ）
- **Instant**: 力制限やコンプライアンスなし
- **Runtime**: 実行中に動的に追加/削除可能
