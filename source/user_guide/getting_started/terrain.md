# 🏔️ 地形シミュレーションと生成

Genesis は、`gs.morphs.Terrain` morph により **height-field 地形** を第一級サポートします。
地形は、内部的には高さマップ（高速な衝突問い合わせ用）と watertight 三角形メッシュ（可視化および SDF 生成用）で表現される静的剛体です。

このページでは、地形を作成する代表的な 3 つの方法を紹介します。

1. 独自の NumPy 高さマップを渡す
2. *sub-terrain* グリッドを手続き生成する（Isaac Gym スタイル）
3. 任意の三角形メッシュを自動で高さマップへ変換する

---

## 1 独自の高さマップを使う
既に地形データ（例えば DEM ファイル由来）がある場合、Genesis へ直接渡せます。
必要なのは水平スケールと垂直スケールの 2 つです。

```python
import numpy as np
import genesis as gs

# 1. initialise Genesis
gs.init(seed=0, backend=gs.gpu)  # use gs.cpu for CPU backend

# 2. create a scene
scene = gs.Scene(show_viewer=True)

# 3. prepare a height map (here a simple bump for demo)
hf = np.zeros((40, 40), dtype=np.int16)
hf[10:30, 10:30] = 200 * np.hanning(20)[:, None] * np.hanning(20)[None, :]

horizontal_scale = 0.25  # metres between grid points
vertical_scale   = 0.005  # metres per height-field unit

# 4. add the terrain entity
scene.add_entity(
    morph=gs.morphs.Terrain(
        height_field=hf,
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
    ),
)

scene.build()

# run the sim so you can inspect the surface
for _ in range(1_000):
    scene.step()
```

### 可視化デバッグのヒント
シーンをビルドすると、高さマップは `terrain.geoms[0].metadata["height_field"]` に保存されます。
各サンプル位置へ小球を描画すれば、実際の形状を確認できます。

```python
import torch

hf = terrain.geoms[0].metadata["height_field"]
rows = horizontal_scale * torch.arange(hf.shape[0]).unsqueeze(1).repeat(1, hf.shape[1])
cols = horizontal_scale * torch.arange(hf.shape[1]).unsqueeze(0).repeat(hf.shape[0], 1)
heights = vertical_scale * torch.tensor(hf)
poss = torch.stack((rows, cols, heights), dim=-1).reshape(-1, 3)
scene.draw_debug_spheres(poss, radius=0.05, color=(0, 0, 1, 0.7))
```

---

## 2 手続き的サブテレイン
`gs.morphs.Terrain` は、*sub-terrain* タイルを格子状に敷き詰めることで複雑な地面を **合成** できます。
これは Isaac Gym と同じ手法です。指定するのは次の 3 つです。

* `n_subterrains=(nx, ny)` – 各方向のタイル数
* `subterrain_size=(sx, sy)` – 各タイルのサイズ（m）
* `subterrain_types` – タイルごとの生成器を指定する 2 次元リスト

組み込み生成器の一覧:
`flat_terrain`, `random_uniform_terrain`, `pyramid_sloped_terrain`, `discrete_obstacles_terrain`, `wave_terrain`, `pyramid_stairs_terrain`, `stairs_terrain`, `stepping_stones_terrain`, `fractal_terrain`。

```python
scene = gs.Scene(show_viewer=True)

terrain = scene.add_entity(
    morph=gs.morphs.Terrain(
        n_subterrains=(2, 2),
        subterrain_size=(6.0, 6.0),
        horizontal_scale=0.25,
        vertical_scale=0.005,
        subterrain_types=[
            ["flat_terrain", "random_uniform_terrain"],
            ["pyramid_sloped_terrain", "discrete_obstacles_terrain"],
        ],
    ),
)

scene.build(n_envs=100)  # you can still run many parallel envs
```

上のコードは、Genesis に同梱される `examples/rigid/terrain_subterrain.py` と本質的に同じです。
完全な実行可能スクリプトはそちらを参照してください。

---

## 3 三角形メッシュから高さマップを生成する
詳細な CAD やフォトグラメトリメッシュを持っていて、衝突だけ高速化したい場合があります。
`genesis.utils.terrain.mesh_to_heightfield` は、メッシュを鉛直レイでサンプリングし、NumPy の高さ配列とグリッド座標を返します。

```python
from genesis.utils.terrain import mesh_to_heightfield
import os

# path to your .obj / .glb / .stl terrain
mesh_path = os.path.join(gs.__path__[0], "assets", "meshes", "terrain_45.obj")

horizontal_scale = 2.0  # desired grid spacing (metres)
height, xs, ys = mesh_to_heightfield(mesh_path, spacing=horizontal_scale, oversample=3)

# shift the terrain so the centre of the mesh becomes (0,0)
translation = np.array([xs.min(), ys.min(), 0.0])

scene = gs.Scene(show_viewer=True)
scene.add_entity(
    morph=gs.morphs.Terrain(
        height_field=height,
        horizontal_scale=horizontal_scale,
        vertical_scale=1.0,
        pos=translation,  # optional world transform
    ),
)
scene.add_entity(gs.morphs.Sphere(pos=(10, 15, 10), radius=1))
scene.build()
```

この手順は `examples/rigid/terrain_from_mesh.py` にまとめられています。

---

## API リファレンス
キーワード引数の完全な一覧は、自動生成 API ページを参照してください。

```{eval-rst}
.. autoclass:: genesis.options.morphs.Terrain
   :members:
   :show-inheritance:
```

---

### 地形の保存と再利用
地形作成時、Genesis は高さマップ、衝突判定用 watertight メッシュ、表示用簡略メッシュを生成します。
`name="my_terrain"` を渡すと、高さマップのキャッシュを有効化できます。
同一オプションで次回生成時は再生成せずキャッシュを読み込むため、ランダム化地形を厳密に再現したい場合に有用です。

---

地形づくりを楽しんでください。
