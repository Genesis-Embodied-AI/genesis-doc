# 🌊 剛体を超えて

Genesisは複数の物理シミュレーターを統合し、リジッドボディダイナミクスを超えたシミュレーションをサポートしています。`solver`は、特定の材料セットを処理するための物理シミュレーションアルゴリズムの集合体です。このチュートリアルでは、3つの一般的なソルバーを使用して、異なる物理特性を持つエンティティをシミュレーションします。
- [スムースパーティクルハイドロダイナミクス（SPH）ソルバー](#sph)
- [マテリアルポイント法（MPM）ソルバー](#mpm)
- [位置ベースダイナミクス（PBD）ソルバー](#pbd)

## SPHソルバーを使用した液体シミュレーション <a id="sph"></a>
まず、水の立方体をどのようにシミュレーションするかを見てみましょう。空のシーンを作成し、通常通り平面を追加します:
```python
import genesis as gs

########################## 初期化 ##########################
gs.init()

########################## シーンの作成 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    sph_options=gs.options.SPHOptions(
        lower_bound   = (-0.5, -0.5, 0.0),
        upper_bound   = (0.5, 0.5, 1),
        particle_size = 0.01,
    ),
    vis_options=gs.options.VisOptions(
        visualize_sph_boundary = True,
    ),
    show_viewer = True,
)

########################## エンティティ ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)
```

いくつか注意すべき点があります：
- `sim_options`を設定するときに、`dt`を小さくし、`substeps=10`に設定しています。これは、シミュレータ内で各`step`ごとに10個の`substep`をシミュレートし、それぞれの`substep_dt`が`4e-3 / 10`になることを意味します。以前、リジッドボディを扱っていたときは、この設定を行わず、デフォルト設定（`substeps=1`）を使用していました。
- `sph_options`を使用して、SPHソルバーのプロパティを設定しています。この例では、ソルバーの境界を設定し、粒子サイズを0.01mに指定しました。SPHソルバーはラグランジュ法のソルバーで、粒子を使用してオブジェクトを表現します。
- `vis_options`で、レンダリングビューでSPHソルバーの境界を表示するように指定しました。

次に水のブロックエンティティを追加し、シミュレーションを開始します！ブロックを追加する際、リジッドブロックを水のブロックに変える唯一の違いは、`material`を設定することです。以前は`gs.materials.Rigid()`がデフォルトで設定されていましたが、液体シミュレーションには`SPH`カテゴリの`Liquid`マテリアルを選択します。

```python
liquid = scene.add_entity(
    material=gs.materials.SPH.Liquid(
        sampler='pbs',
    ),
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.65),
        size = (0.4, 0.4, 0.4),
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 0.8, 1.0),
        vis_mode = 'particle',
    ),
)

########################## ビルド ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()
```

`Liquid`マテリアルを作成する際、`sampler='pbs'`を設定しました。これは、`Box`モーフから粒子をサンプリングする方法を設定するものです。`pbs`は「物理ベースサンプリング」を意味し、粒子が物理的に自然な配置になるようにいくつかの追加のシミュレーションステップを実行します。単純なグリッドパターンを使用したい場合は、`'regular'`サンプラーを使用できます。他のソルバー（例：MPM）を使用する場合、`'random'`サンプラーを使用することも可能です。

また、`surface`属性を指定してエンティティの視覚的プロパティを定義しました。ここでは水の色を青に設定し、`vis_mod='particle'`で粒子として表示するようにしました。

これを実行すると、水が平面に落ちて広がり、ソルバーの境界内に制約されているのが見られます。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/sph_liquid.mp4" type="video/mp4">
</video>

リアルタイムで粒子の位置を取得するには以下を使用します:
```python
particles = liquid.get_particles()
```

**液体のプロパティを変更する:** 液体の粘性（`mu`）や表面張力（`gamma`）を変更して、挙動の違いを確認することができます:
```python
material=gs.materials.SPH.Liquid(mu=0.02, gamma=0.02),
```

試してみてください！

完全なスクリプト:
```python
import genesis as gs

########################## 初期化 ##########################
gs.init()

########################## シーンの作成 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    sph_options=gs.options.SPHOptions(
        lower_bound   = (-0.5, -0.5, 0.0),
        upper_bound   = (0.5, 0.5, 1),
        particle_size = 0.01,
    ),
    vis_options=gs.options.VisOptions(
        visualize_sph_boundary = True,
    ),
    show_viewer = True,
)

########################## エンティティ ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)

liquid = scene.add_entity(
    # 粘性のある液体
    # material=gs.materials.SPH.Liquid(mu=0.02, gamma=0.02),
    material=gs.materials.SPH.Liquid(),
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.65),
        size = (0.4, 0.4, 0.4),
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 0.8, 1.0),
        vis_mode = 'particle',
    ),
)

########################## ビルド ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()

# 粒子の位置を取得
particles = liquid.get_particles()
```

## MPMソルバーを用いた変形可能オブジェクトのシミュレーション <a id="mpm"></a>

MPMソルバーは、幅広い材料をサポートする非常に強力な物理シミュレーションソルバーです。MPMは「Material Point Method（マテリアルポイント法）」の略で、ラグランジュ-オイラーのハイブリッド表現（つまり、粒子とグリッドの両方）を使用してオブジェクトを表現します。

この例では、次の3つのオブジェクトを作成します：
- `'particles'`として可視化される弾性立方体
- `'particles'`として可視化される液体立方体
- 内部粒子状態に基づいて変形される元の球メッシュ（`vis_mode='visual'`）として可視化されるエラストプラスチック球  
  このような、内部粒子状態を変形された視覚メッシュにマッピングするプロセスは、コンピュータグラフィックスでは*スキニング*と呼ばれます。

完全なコードスクリプト：
```python
import genesis as gs

########################## 初期化 ##########################
gs.init()

########################## シーンの作成 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound   = (-0.5, -1.0, 0.0),
        upper_bound   = (0.5, 1.0, 1),
    ),
    vis_options=gs.options.VisOptions(
        visualize_mpm_boundary = True,  # MPMソルバーの境界を可視化
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_fov=30,  # カメラの視野角
    ),
    show_viewer = True,  # ビューアを表示
)

########################## エンティティ ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),  # 平面の形状
)

obj_elastic = scene.add_entity(
    material=gs.materials.MPM.Elastic(),  # 弾性材料
    morph=gs.morphs.Box(
        pos  = (0.0, -0.5, 0.25),  # 位置
        size = (0.2, 0.2, 0.2),    # サイズ
    ),
    surface=gs.surfaces.Default(
        color    = (1.0, 0.4, 0.4),  # 色
        vis_mode = 'visual',         # 視覚モード
    ),
)

obj_sand = scene.add_entity(
    material=gs.materials.MPM.Liquid(),  # 液体材料
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.25),    # 位置
        size = (0.3, 0.3, 0.3),     # サイズ
    ),
    surface=gs.surfaces.Default(
        color    = (0.3, 0.3, 1.0),  # 色
        vis_mode = 'particle',       # 粒子として可視化
    ),
)

obj_plastic = scene.add_entity(
    material=gs.materials.MPM.ElastoPlastic(),  # エラストプラスチック材料
    morph=gs.morphs.Sphere(
        pos  = (0.0, 0.5, 0.35),  # 位置
        radius = 0.1,             # 半径
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 1.0, 0.4),  # 色
        vis_mode = 'particle',       # 粒子として可視化
    ),
)

########################## シーンの構築 ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()  # シーンを進める
```

物理的な材料を変更するには、`material`属性を変更するだけで十分です。他の材料タイプ（例えば、`MPM.Sand()`や`MPM.Snow()`）や、それぞれの材料タイプのプロパティ値を試してみてください。

期待されるレンダリング結果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/mpm.mp4" type="video/mp4">
</video>

# PBD（Position Based Dynamics）ソルバーを使用した布シミュレーション <a id="pbd"></a>

PBDはPosition Based Dynamicsの略です。これはラグランジアンソルバーの一種で、パーティクルとエッジを使用してエンティティを表現し、位置ベースの制約を解くことで状態をシミュレーションします。トポロジーを保持する1D/2D/3Dのエンティティのシミュレーションに使用できます。この例では、PBDソルバーを使用して布のシミュレーションを行う方法を見ていきます。

この例では、2つの正方形の布エンティティを追加します：1つは4つの角を固定し、もう1つは1つの角のみを固定して最初の布の上に落下させます。さらに、異なる`vis_mode`を使用してレンダリングを行います。

シーンの作成とビルド：

```python
import genesis as gs
########################## 初期化 ##########################
gs.init()
########################## シーンの作成 ##########################
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt = 4e-3,
        substeps = 10,
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_fov = 30,
        res = (1280, 720),
        max_FPS = 60,
    ),
    show_viewer = True,
)
########################## エンティティ ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)
cloth_1 = scene.add_entity(
    material=gs.materials.PBD.Cloth(),
    morph=gs.morphs.Mesh(
        file='meshes/cloth.obj',
        scale=2.0,
        pos=(0, 0, 0.5),
        euler=(0.0, 0, 0.0),
    ),
    surface=gs.surfaces.Default(
        color=(0.2, 0.4, 0.8, 1.0),
        vis_mode='visual',
    )
)
cloth_2 = scene.add_entity(
    material=gs.materials.PBD.Cloth(),
    morph=gs.morphs.Mesh(
        file='meshes/cloth.obj',
        scale=2.0,
        pos=(0, 0, 1.0),
        euler=(0.0, 0, 0.0),
    ),
    surface=gs.surfaces.Default(
        color=(0.8, 0.4, 0.2, 1.0),
        vis_mode='particle',
    )
)
########################## ビルド ##########################
scene.build()
```

次に、固定したい角（パーティクル）を固定します。これを行うために、デカルト座標系での位置を使用してパーティクルを特定するための便利なツールを提供しています：

```python
cloth_1.fix_particle(cloth_1.find_closest_particle((-1, -1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((1, 1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((-1, 1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((1, -1, 1.0)))
cloth_2.fix_particle(cloth_2.find_closest_particle((-1, -1, 1.0)))
horizon = 1000
for i in range(horizon):
    scene.step()
```

期待されるレンダリング結果：
<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/pbd_cloth.mp4" type="video/mp4">
</video>

:::{warning}
**2Dメッシュのスキニング**
2Dの平面布メッシュを使用し、`vis_mode='visual'`を設定した場合、バリセントリック重みを計算する際の擬似逆行列計算で問題が発生することに気づきました。上記の例で布にゼロでないeulerを追加し、`vis_mode='visual'`を使用すると、奇妙な視覚化結果が表示される場合があります。これは近日中に修正される予定です。
:::

***ソルバー間カップリングに関するチュートリアルは近日公開予定です！***