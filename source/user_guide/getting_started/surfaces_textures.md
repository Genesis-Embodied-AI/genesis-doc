# 🎨 サーフェスとテクスチャ

Genesis は、レンダリングのためのマテリアルおよびテクスチャ設定を提供します。

## サーフェスタイプ

| サーフェス | 説明 |
|---------|-------------|
| `Rough` | マットで非反射（roughness=1.0） |
| `Smooth` | 研磨されたプラスチック（roughness=0.1） |
| `Reflective` | 高反射（roughness=0.01） |
| `Glass` | 屈折を伴う透明サーフェス |
| `Metal` | 金属サーフェス（Iron、Gold など） |
| `Water` | 水面ライクなサーフェス |
| `Emission` | 発光サーフェス |

## 基本的な使い方

```python
import genesis as gs

scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0, 0, 1), radius=0.5),
    surface=gs.surfaces.Smooth(color=(0.8, 0.2, 0.2)),
)
```

## サーフェスプロパティ

```python
gs.surfaces.Smooth(
    color=(1.0, 1.0, 1.0),    # RGB (0-1)
    roughness=0.1,            # 0=鏡面, 1=マット
    metallic=0.0,             # 0=誘電体, 1=金属
    opacity=1.0,              # 透明度
    emissive=(0.0, 0.0, 0.0), # 自己発光
    ior=1.5,                  # 屈折率
)
```

## 金属サーフェス

```python
# 既定の金属
gs.surfaces.Iron()
gs.surfaces.Gold()
gs.surfaces.Copper()
gs.surfaces.Aluminium()

# カスタム金属
gs.surfaces.Metal(metal_type="gold", roughness=0.15)
```

## 透明サーフェス

```python
# Glass
gs.surfaces.Glass(
    color=(0.9, 0.9, 1.0, 0.7),  # RGBA
    roughness=0.1,
    ior=1.5,
)

# Water
gs.surfaces.Water()
```

## テクスチャ

### カラーテクスチャ

```python
gs.textures.ColorTexture(color=(1.0, 0.0, 0.0))
```

### 画像テクスチャ

```python
gs.textures.ImageTexture(
    image_path="textures/checker.png",
    encoding="srgb",  # 非色情報の場合は "linear"
)
```

### サーフェスとテクスチャを組み合わせる

```python
surface = gs.surfaces.Rough(
    diffuse_texture=gs.textures.ImageTexture(image_path="albedo.png"),
    roughness_texture=gs.textures.ImageTexture(image_path="roughness.png", encoding="linear"),
    normal_texture=gs.textures.ImageTexture(image_path="normal.png", encoding="linear"),
)
```

## 可視化モード

```python
# 粒子可視化（流体系向け）
gs.surfaces.Rough(color=(0.6, 0.8, 1.0), vis_mode="particle")

# サーフェス再構成
gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7), vis_mode="recon")
```

## 環境マップ（Raytracer）

```python
scene = gs.Scene(
    renderer=gs.renderers.RayTracer(
        env_surface=gs.surfaces.Emission(
            emissive_texture=gs.textures.ImageTexture(image_path="hdri.hdr")
        ),
        env_radius=15.0,
    )
)
```
