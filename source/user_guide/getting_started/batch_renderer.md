# 🎬 バッチレンダラー

BatchRenderer は、Madrona の GPU バッチレンダリングを使って、高スループットなマルチ環境シミュレーションを実現します。

## インストール

```bash
pip install gs-madrona
```

**要件:** Linux x86-64、NVIDIA CUDA、Python >= 3.10

## 基本設定

```python
import genesis as gs

gs.init(backend=gs.cuda)  # CUDA が必要

scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(use_rasterizer=True),
)

plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# すべてのバッチカメラは同一解像度である必要があります
cam1 = scene.add_camera(res=(256, 256), pos=(2, 0, 1), lookat=(0, 0, 0.5))
cam2 = scene.add_camera(res=(256, 256), pos=(0, 2, 1), lookat=(0, 0, 0.5))

scene.build(n_envs=128)
```

## レンダリング

```python
for step in range(1000):
    scene.step()

    # 単一カメラをレンダリング
    rgb, depth, seg, normal = cam1.render(
        rgb=True, depth=True, segmentation=True, normal=True
    )
    # 形状: (n_envs, H, W, C)

    # または全カメラを一度にレンダリング
    all_rgb = scene.render_all_cameras(rgb=True)
    # 形状: (n_cameras, n_envs, H, W, 3)
```

## カメラセンサー API

```python
camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
        near=0.1,
        far=100.0,
        lights=[{
            "pos": (2.0, 2.0, 5.0),
            "color": (1.0, 1.0, 1.0),
            "intensity": 1.0,
            "directional": True,
            "castshadow": True,
        }],
    )
)

scene.build(n_envs=64)

data = camera.read()  # .rgb テンソルを持つ CameraData を返します
```

## ライティング

```python
scene.add_light(
    pos=(0.0, 0.0, 3.0),
    dir=(0.0, 0.0, -1.0),
    color=(1.0, 1.0, 1.0),
    intensity=1.0,
    directional=True,
    castshadow=True,
)
```

## セグメンテーション

```python
scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(),
    vis_options=gs.options.VisOptions(
        segmentation_level="link",  # "entity"、"link"、または "geom"
    ),
)

# レンダリング後
_, _, seg, _ = camera.render(segmentation=True)
colored = scene.visualizer.colorize_seg_idxc_arr(seg)
```

## パフォーマンスのヒント

- すべてのカメラで同一解像度を使用する
- 速度重視なら `use_rasterizer=True` を優先する
- `scene.render_all_cameras()` で全カメラをバッチレンダリングする
- 典型的な構成: 256x256 解像度、128〜256 環境
