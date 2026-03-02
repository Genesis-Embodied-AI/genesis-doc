# 📷 カメラセンサー

Genesis は、シミュレーション内で RGB 画像をレンダリングするための 3 種類のカメラセンサーバックエンドを提供します。

## カメラセンサーの種類

| センサー | バックエンド | マルチ環境対応 | 用途 |
|--------|---------|-----------|----------|
| `RasterizerCameraSensor` | OpenGL | 逐次 | 高速リアルタイムレンダリング |
| `RaytracerCameraSensor` | LuisaRender | 単一環境のみ | フォトリアル画像 |
| `BatchRendererCameraSensor` | Madrona GPU | 並列 | 高スループット RL 学習 |

## 基本的な使い方

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(morph=gs.morphs.Plane())

# カメラセンサーを追加
camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
    )
)

scene.build(n_envs=1)
scene.step()

# レンダリング画像を取得
data = camera.read()
print(data.rgb.shape)  # 単一環境では (512, 512, 3)
```

## カメラオプション

### 共通パラメータ（全バックエンド共通）

```python
gs.sensors.RasterizerCameraOptions(
    res=(512, 512),              # (width, height)
    pos=(3.0, 0.0, 2.0),         # 位置（固定または取り付けリンク基準）
    lookat=(0.0, 0.0, 0.0),      # 注視点
    up=(0.0, 0.0, 1.0),          # 上方向ベクトル
    fov=60.0,                    # 垂直 FOV（度）
    entity_idx=-1,               # 取り付け対象エンティティ（-1 = 固定）
    link_idx_local=0,            # 取り付けリンクインデックス
)
```

### Raytracer 固有オプション

```python
gs.sensors.RaytracerCameraOptions(
    model="pinhole",             # "pinhole" または "thinlens"
    spp=256,                     # 1 ピクセルあたりサンプル数
    denoise=False,               # デノイズを適用
    aperture=2.8,                # 被写界深度（thinlens）
    focus_dist=3.0,              # 焦点距離（thinlens）
)
```

### BatchRenderer 固有オプション

```python
gs.sensors.BatchRendererCameraOptions(
    near=0.01,                   # 近クリップ面
    far=100.0,                   # 遠クリップ面
    use_rasterizer=True,         # GPU ラスタライザモード
)
```

**注意:** BatchRenderer カメラはすべて同一解像度である必要があります。

## エンティティへのカメラ取り付け

ロボットのエンドエフェクタにカメラを搭載する例です。

```python
robot = scene.add_entity(morph=gs.morphs.URDF(file="robot.urdf"))

camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(640, 480),
        pos=(0.1, 0.0, 0.05),    # リンク座標系からのオフセット
        lookat=(0.2, 0.0, 0.0),  # 視線方向
        entity_idx=robot.idx,    # ロボットに取り付け
        link_idx_local=8,        # エンドエフェクタリンク
    )
)
```

カメラはエンティティの動きに自動追従します。

## マルチ環境レンダリング

```python
scene.build(n_envs=4)

# 環境ごとに異なる状態を設定
sphere.set_pos([[0, 0, 1], [0.2, 0, 1], [0.4, 0, 1], [0.6, 0, 1]])
scene.step()

# 全環境を取得
data = camera.read()
print(data.rgb.shape)  # (4, H, W, 3)

# 特定環境のみ取得
data = camera.read(envs_idx=[0, 2])
print(data.rgb.shape)  # (2, H, W, 3)
```

## バックエンドの選び方

- **Rasterizer**: デフォルト選択。高速で全プラットフォームで利用可能
- **Raytracer**: フォトリアルが必要な場合に使用（`renderer=gs.renderers.RayTracer()` が必要）
- **BatchRenderer**: 多環境 RL 学習向け（CUDA のみ）

```python
# raytracer 用: scene renderer を設定
scene = gs.Scene(renderer=gs.renderers.RayTracer())

# batch renderer 用
scene = gs.Scene(renderer=gs.renderers.BatchRenderer())
```
