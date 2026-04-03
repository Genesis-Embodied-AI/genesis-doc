# 🧗 高度で並列なIK（逆運動学）

GenesisのIKソルバーは多くの強力な機能を備えています。この例では、柔軟な目標姿勢を受け入れるようにIKソルバーを設定する方法と、バッチ環境でロボットのIKを解く方法を示します。

## 複数のエンドエフェクタリンクを使用したIK

この例では、ロボットグリッパーの左指と右指を2つの個別のターゲットリンクとして使用します。さらに、それぞれのリンクの目標姿勢として完全な6自由度（6-DoF）の姿勢を使用する代わりに、グリッパーの位置とz軸方向のみを考慮して解きます。

```python
import numpy as np

import genesis as gs

########################## 初期化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

########################## シーンの作成 ##########################
scene = gs.Scene(
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(2.0, -2, 1.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit=False,
        enable_collision=False,
    ),
)

########################## エンティティ ##########################

scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

# 可視化用の2つのターゲットリンク
target_left = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/axis.obj',
        scale=0.1,
    ),
    surface=gs.surfaces.Default(color=(1, 0.5, 0.5, 1)),
)
target_right = scene.add_entity(
    gs.morphs.Mesh(
        file='meshes/axis.obj',
        scale=0.1,
    ),
    surface=gs.surfaces.Default(color=(0.5, 1.0, 0.5, 1)),
)

########################## ビルド ##########################
scene.build()

target_quat = np.array([0, 1, 0, 0])
center = np.array([0.4, -0.2, 0.25])
r = 0.1

left_finger = robot.get_link('left_finger')
right_finger = robot.get_link('right_finger')

for i in range(0, 2000):
    target_pos_left = center + np.array([np.cos(i/360*np.pi), np.sin(i/360*np.pi), 0]) * r
    target_pos_right = target_pos_left + np.array([0.0, 0.03, 0])

    target_left.set_qpos(np.concatenate([target_pos_left, target_quat]))
    target_right.set_qpos(np.concatenate([target_pos_right, target_quat]))
    
    q = robot.inverse_kinematics_multilink(
        links    = [left_finger, right_finger],
        poss     = [target_pos_left, target_pos_right],
        quats    = [target_quat, target_quat],
        rot_mask = [False, False, True], # z軸方向のみを制約
    )

    # このIKは可視化目的のため、ここではscene.step()を呼び出さず、状態とビジュアライザーを更新するだけです。
    # 実際の制御アプリケーションでは、代わりにrobot.control_dofs_position()とscene.step()を使用する必要があります。
    robot.set_dofs_position(q)
    scene.visualizer.update()
```

このような動作が表示されます：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/ik_multilink.mp4" type="video/mp4">
</video>

この例から学べる新しい点は以下の通りです：
- `robot.inverse_kinematics_multilink()` APIを使用して、複数のターゲットリンクを考慮したIKを解きました。このAPIを使用する際には、ターゲットリンクオブジェクトのリスト、ターゲット位置のリスト、ターゲット姿勢（クォータニオン）のリストを渡します。
- `rot_mask`を使用して、不要な軸方向の回転をマスクしました。この例では、両指が下向き（z軸が下向き）になるようにしたいですが、水平方向の回転についてはそれほど制約を課していません。この`rot_mask`を柔軟に使用することで、目的の姿勢を実現できます。同様に、x/y/z軸方向の位置をマスクするための`pos_mask`も利用できます。
- この例は物理演算を含まないため、ロボットと2つのターゲットリンクの位置を設定した後、`scene.step()`を呼び出す必要はありません。代わりに、`scene.visualizer.update()`を呼び出して、ビューワー（およびカメラ）の変更を反映させます。
- **qposとは？** この例ではターゲットリンクの状態を設定するために`set_qpos`を使用しました。`qpos`はエンティティの一般化座標での構成を表します。単一のアームの場合、その`qpos`は`dofs_position`と同一であり、すべてのジョイント（回転+直動）に1自由度（dof）しかありません。一方、自由ジョイントを介して`world`に接続された自由メッシュの場合、このジョイントには6自由度（3つの並進+3つの回転）があり、その一般化座標`q`は7次元ベクトル（xyz並進+wxyzクォータニオン）になります。そのため、`qpos`は`dofs_position`と異なります。この状態を設定するには`set_qpos()`または`set_dofs_position()`のどちらも使用できますが、この例ではクォータニオンを既に知っているため、`qpos`を計算する方が簡単です。この違いは、回転を3次元ベクトル（3軸周りの回転）または4次元ベクトル（wxyzクォータニオン）のいずれかで表現できる点から来ています。

## 並列シミュレーション用のIK

Genesisでは、バッチ環境内でもIKを解くことができます。16個の並列環境を生成し、それぞれのロボットのエンドエフェクタが異なる角速度で回転するように設定してみましょう：

```python
import numpy as np
import genesis as gs

########################## 初期化 ##########################
gs.init()

########################## シーンの作成 ##########################
scene = gs.Scene(
    viewer_options= gs.options.ViewerOptions(
        camera_pos    = (0.0, -2, 1.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 200,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_joint_limit = False,
    ),
)

########################## エンティティ ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)
robot = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## ビルド ##########################
n_envs = 16
scene.build(n_envs=n_envs, env_spacing=(1.0, 1.0))

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1]) # 下向き
center = np.tile(np.array([0.4, -0.2, 0.25]), [n_envs, 1])
angular_speed = np.random.uniform(-10, 10, n_envs)
r = 0.1

ee_link = robot.get_link('hand')

for i in range(0, 1000):
    target_pos = np.zeros([n_envs, 3])
    target_pos[:, 0] = center[:, 0] + np.cos(i/360*np.pi*angular_speed) * r
    target_pos[:, 1] = center[:, 1] + np.sin(i/360*np.pi*angular_speed) * r
    target_pos[:, 2] = center[:, 2]
    target_q = np.hstack([target_pos, target_quat])

    q = robot.inverse_kinematics(
        link     = ee_link,
        pos      = target_pos,
        quat     = target_quat,
        rot_mask = [False, False, True], # デモ目的: z軸方向のみを制約
    )

    robot.set_qpos(q)
    scene.step()
```

並列環境を扱う際は、目標姿勢変数にバッチ次元を追加することを確認してください。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/batched_IK.mp4" type="video/mp4">
</video>
