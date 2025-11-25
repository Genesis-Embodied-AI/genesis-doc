# 🐛 ソフトロボット

## ボリューム筋肉シミュレーション

Genesisでは、ソフトロボットのためのMPMおよびFEMを使用したボリューム筋肉シミュレーションをサポートしています。以下の例では、正弦波制御信号で駆動される球体のボディを持つ非常にシンプルなソフトロボットを示しています。

```python
import numpy as np
import genesis as gs


########################## 初期化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

########################## シーンを作成 ##########################
dt = 5e-4
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        substeps=10,
        gravity=(0, 0, 0),
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 0, 0.8),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    mpm_options=gs.options.MPMOptions(
        dt=dt,
        lower_bound=(-1.0, -1.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
    ),
    fem_options=gs.options.FEMOptions(
        dt=dt,
        damping=45.,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=False,
    ),
)

########################## エンティティ ##########################
scene.add_entity(morph=gs.morphs.Plane())

E, nu = 3.e4, 0.45
rho = 1000.

robot_mpm = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, 0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.MPM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='neohooken',
    ),
)

robot_fem = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, -0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.FEM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='stable_neohooken',
    ),
)

########################## 構築 ##########################
scene.build()

########################## 実行 ##########################
scene.reset()
for i in range(1000):
    # 制御信号を生成
    actu = np.array([0.2 * (0.5 + np.sin(0.01 * np.pi * i))])

    # 筋肉の駆動を設定
    robot_mpm.set_actuation(actu)
    robot_fem.set_actuation(actu)
    scene.step()
```

以下のような結果が得られます：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/muscle.mp4" type="video/mp4">
</video>

ほとんどのコードは通常の変形可能エンティティをインスタンス化するのと比較して標準的ですが、以下の2つの違いがあります：

* ソフトロボット `robot_mpm` と `robot_fem` をインスタンス化する際に、それぞれ `gs.materials.MPM.Muscle` と `gs.materials.FEM.Muscle` を使用します。
* シミュレーションを進める際には、筋肉の駆動を設定するために `robot_mpm.set_actuation` または `robot_fem.set_actuation` を使用します。

デフォルトでは、ロボット全体のボディをカバーする筋肉が1つだけあり、筋肉の方向は地面に対して垂直（`[0, 0, 1]`）に設定されています。

次の例では、筋肉のグループと方向を設定することで、ミミズが前方に這う動きをシミュレーションする方法を示します（完全なスクリプトは [tutorials/advanced_worm.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/examples/tutorials/advanced_worm.py) にあります）。

```python
########################## エンティティ ##########################
worm = scene.add_entity(
    morph=gs.morphs.Mesh(
        file='meshes/worm/worm.obj',
        pos=(0.3, 0.3, 0.001),
        scale=0.1,
        euler=(90, 0, 0),
    ),
    material=gs.materials.MPM.Muscle(
        E=5e5,
        nu=0.45,
        rho=10000.,
        model='neohooken',
        n_groups=4,
    ),
)

########################## 筋肉を設定 ##########################
def set_muscle_by_pos(robot):
    # MPMについては、位置情報を取得して筋肉を設定
    if isinstance(robot.material, gs.materials.MPM.Muscle):
        pos = robot.get_state().pos
        n_units = robot.n_particles
    elif isinstance(robot.material, gs.materials.FEM.Muscle):
        # FEMについては、要素の位置情報を取得
        pos = robot.get_state().pos[robot.get_el2v()].mean(1)
        n_units = robot.n_elements
    else:
        raise NotImplementedError

    pos = pos.cpu().numpy()
    pos_max, pos_min = pos.max(0), pos.min(0)
    pos_range = pos_max - pos_min

    # 上部/下部および前部/後部を分割
    lu_thresh, fh_thresh = 0.3, 0.6
    muscle_group = np.zeros((n_units,), dtype=int)
    mask_upper = pos[:, 2] > (pos_min[2] + pos_range[2] * lu_thresh)
    mask_fore = pos[:, 1] < (pos_min[1] + pos_range[1] * fh_thresh)
    muscle_group[ mask_upper &  mask_fore] = 0 # 上部前方
    muscle_group[ mask_upper & ~mask_fore] = 1 # 上部後方
    muscle_group[~mask_upper &  mask_fore] = 2 # 下部前方
    muscle_group[~mask_upper & ~mask_fore] = 3 # 下部後方

    # 筋肉の方向を定義
    muscle_direction = np.array([[0, 1, 0]] * n_units, dtype=float)

    # 筋肉の設定
    robot.set_muscle(
        muscle_group=muscle_group,
        muscle_direction=muscle_direction,
    )

set_muscle_by_pos(worm)

########################## 実行 ##########################
scene.reset()
for i in range(1000):
    # 筋肉の駆動を設定
    actu = np.array([0, 0, 0, 1. * (0.5 + np.sin(0.005 * np.pi * i))])

    worm.set_actuation(actu)
    scene.step()
```

以下のような結果が得られます：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/worm.mp4" type="video/mp4">
</video>

このコードスニペットの主なポイントは以下の通りです：

* 材料 `gs.materials.MPM.Muscle` を指定する際に、追加の引数 `n_groups = 4` を指定します。これは、このロボットに最大4つの異なる筋肉が存在できることを意味します。
* 筋肉の設定には `robot.set_muscle` を使用します。この関数は `muscle_group` と `muscle_direction` を入力として受け取ります。どちらも長さが `n_units` に一致し、MPMにおける `n_units` は粒子数を、FEMにおける `n_units` は要素数を表します。
    - `muscle_group` は整数の配列（例: `0` から `n_groups - 1`）で、ロボットのボディのユニットが属する筋肉グループを示します。
    - `muscle_direction` は筋肉方向を指定したベクトルの浮動小数点数配列です。
* このミミズの例では、ボディを4つの部分（上部前方、上部後方、下部前方、下部後方）に分割し、`lu_thresh` と `fh_thresh` を使って閾値を設定しました。
* 4つの筋肉グループが設定された後、`set_actuation` を通じて制御信号を設定する際は、入力信号は形状 `(4,)` の配列となります。


## ハイブリッド（剛体とソフトの組み合わせ）ロボット

もう一つのソフトロボットのタイプとして、剛体の内部骨格を使用してソフトな外皮を駆動する、いわばハイブリッドロボットがあります。Genesisはすでに剛体とソフト体の両方の動力学を実装しているため、ハイブリッドロボットにも対応しています。以下の例では、ソフトスキンで覆われた2リンクの骨格を持ち、剛体のボールを押すハイブリッドロボットを示します。

```python
import numpy as np
import genesis as gs


########################## 初期化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

######################## シーンを作成 ########################
dt = 3e-3
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        substeps=10,
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 1.3, 0.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        dt=dt,
        gravity=(0, 0, -9.8),
        enable_collision=True, # 衝突を有効化
        enable_self_collision=False, # 自己衝突を無効化
    ),
    mpm_options=gs.options.MPMOptions(
        dt=dt,
        lower_bound=( 0.0,  0.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
        gravity=(0, 0, 0), # 重力補償を模倣
        enable_CPIC=True,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True, # ワールドフレームを表示
        visualize_mpm_boundary=False, # MPM境界の可視化を無効化
    ),
)

########################## エンティティ ##########################
scene.add_entity(morph=gs.morphs.Plane())

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="urdf/simple/two_link_arm.urdf",
        pos=(0.5, 0.5, 0.3),
        euler=(0.0, 0.0, 0.0),
        scale=0.2,
        fixed=True, # 固定されたロボット
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(
            gravity_compensation=1., # 重力補償
        ),
        material_soft=gs.materials.MPM.Muscle( # 筋肉グループの設定を有効化
            E=1e4,
            nu=0.45,
            rho=1000.,
            model='neohooken',
        ),
        thickness=0.05, # スキンの厚さ
        damping=1000.,
        func_instantiate_rigid_from_soft=None,
        func_instantiate_soft_from_rigid=None,
        func_instantiate_rigid_soft_association=None,
    ),
)

ball = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.8, 0.6, 0.1),
        radius=0.1,
    ),
    material=gs.materials.Rigid(rho=1000, friction=0.5), # 剛体球
)

########################## 構築 ##########################
scene.build()

########################## 実行 ##########################
scene.reset()
for i in range(1000):
    dofs_ctrl = np.array([
        1. * np.sin(2 * np.pi * i * 0.001),
    ] * robot.n_dofs)

    # 自由度の速度を制御
    robot.control_dofs_velocity(dofs_ctrl)

    scene.step()
```

以下のような結果が得られます：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

### ポイント

* ハイブリッドロボットは、`gs.materials.Hybrid` を使用して指定できます。この材料は `gs.materials.Rigid`（剛体）と `gs.materials.MPM.Muscle`（筋肉）の両方から構成されます。ここではMPMのみがサポートされており、`Muscle` クラスである必要があります。これは、ハイブリッド材料が内部的に `Muscle` 用の `muscle_group` 機能を再利用しているためです。
* 制御に関しては、内部の剛体骨格から駆動されるため、剛体ロボットと似たインターフェースを使用します。例えば、`control_dofs_velocity`、`control_dofs_force`、`control_dofs_position` などがあります。また、制御の次元は内部骨格の自由度（DoFs）と同じです（上記の例では2つ）。
* スキンの形状は内部骨格の形状によって決定されます。`thickness` パラメータを使用して骨格を包むスキンの厚みを設定します。
* デフォルトでは、骨格の形状に基づいてスキンを生成します。これは `morph`（この例では `urdf/simple/two_link_arm.urdf`）で指定されています。`gs.materials.Hybrid` の引数 `func_instantiate_soft_from_rigid` は、剛体形状に基づいてスキンを具体的にどのように生成するかを定義します。デフォルトの実装は、[genesis/engine/entities/hybrid_entity.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/entities/hybrid_entity.py) にある `default_func_instantiate_soft_from_rigid` です。独自の関数を実装することも可能です。
* `morph` が `URDF` ではなく `Mesh` の場合、メッシュがソフトな外部形状を指定し、内部骨格はスキンの形状に基づいて生成されます。これは `func_instantiate_rigid_from_soft` で定義されています。デフォルト実装 `default_func_instantiate_rigid_from_soft` もあり、基本的には3Dメッシュのスケルトン化を実装しています。
* `gs.materials.Hybrid` の引数 `func_instantiate_rigid_soft_association` は、それぞれの骨格パーツがスキンとどのように関連付けられるかを決定します。デフォルト実装では、骨格パーツに最も近いスキンの粒子を見つける方法を提供しています。
