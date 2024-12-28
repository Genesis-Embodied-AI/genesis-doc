# 🕹️ ロボットの制御

ロボットを読み込んだので、様々な方法でロボットを制御する方法を包括的な例で見ていきましょう。

いつもどおり、genesisをインポートし、シーンを作成し、frankaロボットを読み込みます：

```python
import numpy as np
import genesis as gs

########################## 初期化 ##########################
gs.init(backend=gs.gpu)

########################## シーンの作成 ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
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

# エンティティを読み込む際、morphで姿勢を指定できます
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
        pos   = (1.0, 1.0, 0.0),
        euler = (0, 0, 0),
    ),
)

########################## ビルド ##########################
scene.build()
```

制御力を与えないと、このロボットアームは重力で落下します。Genesisには、目標関節位置や速度を入力として受け取るPD制御器が組み込まれています。また、各関節に直接トルク/力を設定することもできます。

ロボットシミュレーションの文脈では、「関節（joint）」と「自由度（dof: degree-of-freedom）」は関連しているものの異なる概念です。今回扱うFrankaアームは、アーム部分に7つの回転関節とグリッパーに2つの並進関節を持っており、すべての関節は1自由度のみを持つため、9自由度の関節体となっています。より一般的なケースでは、フリージョイント（6自由度）やボールジョイント（3自由度）のように、複数の自由度を持つ関節タイプも存在します。一般的に、各自由度はモーターとして考えることができ、独立に制御できます。

どの関節（自由度）を制御するかを知るために、URDF/MJCFファイルで（ユーザーとして）定義した関節名をシミュレーター内の実際の自由度インデックスにマッピングする必要があります：

```python
jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]
```

ここでは`.dof_idx_local`を使用して、ロボットエンティティ自体に対する自由度のローカルインデックスを取得しています。また、`joint.dof_idx`を使用して、シーン内の各関節のグローバル自由度インデックスにアクセスすることもできます。

次に、各自由度の制御ゲインを設定できます。これらのゲインは、目標関節位置または速度が与えられた時の実際の制御力の大きさを決定します。通常、これらの情報はインポートされたMJCFまたはURDFファイルから解析されますが、手動でチューニングするか、オンラインで十分にチューニングされた値を参照することをお勧めします：

```python
############ オプション：制御ゲインの設定 ############
# 位置ゲインの設定
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# 速度ゲインの設定
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# 安全のための力の範囲設定
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
```

これらのAPIは一般的に、2つの入力値を受け取ります：設定する実際の値と、対応する自由度のインデックスです。ほとんどの制御関連APIはこの規則に従っています。

次に、物理的に現実的なPD制御器を使用する代わりに、まずロボットの構成を手動で設定する方法を見てみましょう。これらのAPIは物理法則に従わずにロボットの状態を突然変更することができます：

```python
# ハードリセット
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()
```

ビューアーをオンにしている場合、50ステップごとにロボットの状態が変化するのが見えるはずです。

次に、組み込みのPD制御器を使ってロボットを制御してみましょう。GenesisのAPI設計は構造化されたパターンに従っています。`set_dofs_position`を使って自由度の位置を直接設定しました。ここでは、`set_*`を`control_*`に変更して、対応する制御器APIを使用します。以下で、ロボットを制御するさまざまな方法を示します：

```python
# PD制御
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # 最初の自由度を速度で制御し、残りを位置で制御
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # これは与えられた制御コマンドに基づいて計算された制御力です
    # 力制御を使用している場合、これは与えられた制御コマンドと同じです
    print('制御力:', franka.get_dofs_control_force(dofs_idx))

    # これは自由度が実際に経験している力です
    print('内部力:', franka.get_dofs_force(dofs_idx))

    scene.step()
```

少し詳しく見ていきましょう：
- ステップ0から500まで、すべての自由度に対して位置制御を使用し、ロボットを3つの目標位置に順次移動させています。`control_*` APIでは、目標値が一度設定されると、内部に保存されるため、目標が同じである限り、以降のステップで繰り返しコマンドをシミュレーションに送る必要はありません。
- ステップ750で、異なる自由度に対して異なる制御が可能であることを示しています：最初の自由度（dof 0）には速度コマンドを送り、残りは位置制御コマンドに従います
- ステップ1000で、トルク（力）制御に切り替え、すべての自由度にゼロ力コマンドを送ると、ロボットは再び重力によって床に落下します。

各ステップの最後に、2種類の力を出力しています：`get_dofs_control_force()`と`get_dofs_force()`です。
- `get_dofs_control_force()`は制御器によって適用される力を返します。位置制御や速度制御の場合、これは目標コマンドと制御ゲインを使用して計算されます。力（トルク）制御の場合、これは入力制御コマンドと同じです。
- `get_dofs_force()`は各自由度が実際に経験する力を返します。これは制御器によって適用される力と、衝突力やコリオリ力などの他の内部力の組み合わせです。

すべてが正しく動作すれば、以下のような結果が見えるはずです：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/control_your_robot.mp4" type="video/mp4">
</video>

上記で説明したすべての内容を含む完全なコードスクリプトは以下の通りです：

```python
import numpy as np

import genesis as gs

########################## 初期化 ##########################
gs.init(backend=gs.gpu)

########################## シーンの作成 ##########################
scene = gs.Scene(
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (0, -3.5, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 30,
        res           = (960, 640),
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
franka = scene.add_entity(
    gs.morphs.MJCF(
        file  = 'xml/franka_emika_panda/panda.xml',
    ),
)
########################## ビルド ##########################
scene.build()

jnt_names = [
    'joint1',
    'joint2',
    'joint3',
    'joint4',
    'joint5',
    'joint6',
    'joint7',
    'finger_joint1',
    'finger_joint2',
]
dofs_idx = [franka.get_joint(name).dof_idx_local for name in jnt_names]

############ オプション：制御ゲインの設定 ############
# 位置ゲインの設定
franka.set_dofs_kp(
    kp             = np.array([4500, 4500, 3500, 3500, 2000, 2000, 2000, 100, 100]),
    dofs_idx_local = dofs_idx,
)
# 速度ゲインの設定
franka.set_dofs_kv(
    kv             = np.array([450, 450, 350, 350, 200, 200, 200, 10, 10]),
    dofs_idx_local = dofs_idx,
)
# 安全のための力の範囲設定
franka.set_dofs_force_range(
    lower          = np.array([-87, -87, -87, -87, -12, -12, -12, -100, -100]),
    upper          = np.array([ 87,  87,  87,  87,  12,  12,  12,  100,  100]),
    dofs_idx_local = dofs_idx,
)
# ハードリセット
for i in range(150):
    if i < 50:
        franka.set_dofs_position(np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]), dofs_idx)
    elif i < 100:
        franka.set_dofs_position(np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]), dofs_idx)
    else:
        franka.set_dofs_position(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), dofs_idx)

    scene.step()

# PD制御
for i in range(1250):
    if i == 0:
        franka.control_dofs_position(
            np.array([1, 1, 0, 0, 0, 0, 0, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 250:
        franka.control_dofs_position(
            np.array([-1, 0.8, 1, -2, 1, 0.5, -0.5, 0.04, 0.04]),
            dofs_idx,
        )
    elif i == 500:
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    elif i == 750:
        # 最初の自由度を速度で制御し、残りを位置で制御
        franka.control_dofs_position(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])[1:],
            dofs_idx[1:],
        )
        franka.control_dofs_velocity(
            np.array([1.0, 0, 0, 0, 0, 0, 0, 0, 0])[:1],
            dofs_idx[:1],
        )
    elif i == 1000:
        franka.control_dofs_force(
            np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
            dofs_idx,
        )
    # これは与えられた制御コマンドに基づいて計算された制御力です
    # 力制御を使用している場合、これは与えられた制御コマンドと同じです
    print('control force:', franka.get_dofs_control_force(dofs_idx))

    # これは自由度が実際に経験している力です 
    print('internal force:', franka.get_dofs_force(dofs_idx))

    scene.step()
```
