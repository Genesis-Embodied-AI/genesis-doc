# 🔺 メッシュ処理

Genesis は、メッシュの読み込み、簡略化、凸分解、衝突処理のためのユーティリティを提供します。

## メッシュの読み込み

```python
import genesis as gs

# ファイルから読み込み
entity = scene.add_entity(gs.morphs.Mesh(file="model.obj"))

# 処理オプション付き
entity = scene.add_entity(
    gs.morphs.Mesh(
        file="model.obj",
        scale=0.1,
        convexify=True,
        decimate=True,
        decimate_face_num=500,
    )
)
```

## デシメーション

衝突処理性能のためにメッシュ複雑度を下げます。

```python
gs.morphs.Mesh(
    file="high_poly.obj",
    decimate=True,
    decimate_face_num=500,         # 目標面数
    decimate_aggressiveness=2,     # 0-8 スケール
)
```

**アグレッシブネス レベル:**
- 0: 無損失
- 2: 形状特徴を保持（デフォルト）
- 5: 大幅削減
- 8: 最大削減

## 凸分解

衝突検出のため、メッシュは凸パーツに分解されます。

```python
gs.morphs.Mesh(
    file="concave.obj",
    convexify=True,  # 必要に応じて自動分解
)
```

Genesis は COACD ライブラリを使い、次のようなオプションを設定できます。

```python
gs.options.COACDOptions(
    threshold=0.05,
    max_convex_hull=16,
    resolution=2000,
    preprocess_mode="auto",
)
```

## 衝突処理

Genesis は衝突メッシュを自動処理します。

1. **修復（Repair）**: 重複面を除去
2. **凸形状化判定（Convexification check）**: 単純凸包で十分か判定
3. **分解（Decomposition）**: 凹メッシュを凸パーツへ分解
4. **簡略化（Decimation）**: 高ポリゴンメッシュを簡略化（>5000 面で警告）

## 四面体化

FEM/変形体シミュレーション向け:

```python
entity = scene.add_entity(
    morph=gs.morphs.Mesh(file="model.obj"),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4),
)
# FEM 用にメッシュは自動で四面体化される
```

## メッシュプロパティ

```python
mesh = entity.morph.mesh

verts = mesh.verts      # (N, 3) 頂点
faces = mesh.faces      # (M, 3) 面インデックス
normals = mesh.normals  # (N, 3) 頂点法線
uvs = mesh.uvs          # (N, 2) テクスチャ座標

is_convex = mesh.is_convex
volume = mesh.volume
area = mesh.area
```

## パーティクルサンプリング

メッシュ体積から粒子をサンプリングします。

```python
mesh.particlize(p_size=0.01, sampler="random")
```

**サンプラー:**
- `"random"`: ランダムサンプリング
- `"pbs_poisson"`: Poisson disk サンプリング
- `"pbs_grid"`: グリッドベースサンプリング

## プリミティブメッシュ

Genesis は組み込みプリミティブを提供します。

```python
gs.morphs.Sphere(radius=0.5)
gs.morphs.Box(size=(1.0, 1.0, 1.0))
gs.morphs.Cylinder(radius=0.3, height=1.0)
gs.morphs.Plane()
```

## キャッシュ

Genesis は処理済みメッシュをキャッシュし、読み込みを高速化します。

| キャッシュ種別 | 拡張子 | 用途 |
|------------|-----------|---------|
| Convex | `.cvx` | 凸分解 |
| Tetrahedral | `.tet` | FEM 四面体化 |
| SDF | `.gsd` | 符号付き距離場 |
| Remesh | `.rm` | リメッシュ版 |
| Particles | `.ptc` | 粒子サンプリング |

キャッシュ無効化判定には入力パラメータの SHA256 ハッシュを使用します。

## 依存関係

- **trimesh**: コアメッシュ操作
- **fast_simplification**: デシメーション
- **coacd**: 凸分解
- **pyvista + tetgen**: 四面体化
