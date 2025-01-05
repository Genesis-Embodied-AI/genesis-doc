# 🦾 逆運動学とモーションプランニング

このチュートリアルでは、Genesis で逆運動学（IK）およびモーションプランニングを使用する方法をいくつかの例を通じて説明し、簡単な把持タスクを実行します。

まず、シーンを作成し、お気に入りのロボットアームと小さなキューブをロードしてシーンを構築し、その後に制御ゲインを設定します：

```python
import numpy as np
import genesis as gs

########################## 初期化 ##########################
gs.init(backend=gs.gpu)

########################## シーンを作成 ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (3, -1, 1.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        max_FPS       = 60,
    ),
    sim_options = gs.options.SimOptions(
        dt = 0.01,
    ),
    show_viewer = True,
)

########################## エンティティ ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
cube = scene.add_entity(
    gs.morphs.Box(
        size = (0.04, 0.04, 0.04),
        pos  = (0.65, 0.0, 0.02),
    )
)
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)
########################## シーンを構築 ##########################
scene.build()

motors_dof = np.arange(7)
fingers_dof = np.arange(7, 9)

# 制御ゲインを設定
# 注意: 以下の値は Franka に最適化された値です
# ロボットごとに異なるパラメータセットが必要になる場合があります。
# 高品質な URDF または XML ファイルが提供されていると、
# それをパースしてパラメータが自動的に設定される場合もあります。
franka.set_dofs_kp(
    np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
)
franka.set_dofs_kv(
    np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
)
franka.set_dofs_force_range(
    np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
)
```

```{figure} ../../_static/images/IK_mp_grasp.png
```

次に、ロボットのエンドエフェクタを把持前の位置へ移動します。これは以下の2ステップで行われます：
- 目標エンドエフェクタの姿勢に基づいて逆運動学（IK）を使用して関節位置を計算
- モーションプランナーを使用して目標位置に到達

Genesis のモーションプランニングには OMPL ライブラリが使用されます。インストール方法については [インストール](../overview/installation.md) ページを参照してください。

Genesis での IK とモーションプランニングはとても簡単で、それぞれ関数呼び出し1回で実行できます。

```python

# エンドエフェクタのリンクを取得
end_effector = franka.get_link('hand')

# 把持前の姿勢へ移動
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.25]),
    quat = np.array([0, 1, 0, 0]),
)
# グリッパーが開いた状態の位置
qpos[-2:] = 0.04
path = franka.plan_path(
    qpos_goal     = qpos,
    num_waypoints = 200, # 2 秒間の移動
)
# 計画された経路を実行
for waypoint in path:
    franka.control_dofs_position(waypoint)
    scene.step()

# ロボットが最後のウェイポイントに到達する時間を確保
for i in range(100):
    scene.step()
```

見ての通り、IK の計算とモーションプランニングはどちらもロボットエンティティの統合メソッドです。IK の場合、ロボットの IK ソルバーにエンドエフェクタのリンクを指定し、目標姿勢を設定するだけです。その後、モーションプランナーに目標関節位置（qpos）を伝えると、計画されたスムーズなウェイポイントリストが返されます。経路を実行した後、コントローラーをさらに100ステップ実行しています。これは、PD コントローラーを使用しているため、目標位置と現在の位置の間に若干のギャップが残る可能性があるからです。そのため、コントローラーを少し長く実行し、ロボットが計画された軌道の最後のウェイポイントに到達できるようにします。

次に、ロボットのグリッパーを下げ、キューブを把持して持ち上げます：

```python
# 到達
qpos = franka.inverse_kinematics(
    link = end_effector,
    pos  = np.array([0.65, 0.0, 0.135]),
    quat = np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(100):
    scene.step()

# 把持
franka.control_dofs_position(qpos[:-2], motors_dof)
franka.control_dofs_force(np.array([-0.5, -0.5]), fingers_dof)

for i in range(100):
    scene.step()

# 持ち上げ
qpos = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.3]),
    quat=np.array([0, 1, 0, 0]),
)
franka.control_dofs_position(qpos[:-2], motors_dof)
for i in range(200):
    scene.step()
```

キューブを把持する際、2つのグリッパー関節（dofs）について力制御を使用し、0.5N の把持力を適用しました。すべてがうまくいけば、キューブが把持され、持ち上げられるのを見ることができます。
