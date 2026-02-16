# 🎨 表面与纹理

Genesis 为渲染提供材质和纹理配置。

## 表面类型

| 表面 | 描述 |
|---------|-------------|
| `Rough` | 哑光，无反光（roughness=1.0） |
| `Smooth` | 抛光塑料（roughness=0.1） |
| `Reflective` | 高反光（roughness=0.01） |
| `Glass` | 带折射的透明材质 |
| `Metal` | 金属表面（铁、金等） |
| `Water` | 水状表面 |
| `Emission` | 发光表面 |

## 基本用法

```python
import genesis as gs

scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0, 0, 1), radius=0.5),
    surface=gs.surfaces.Smooth(color=(0.8, 0.2, 0.2)),
)
```

## 表面属性

```python
gs.surfaces.Smooth(
    color=(1.0, 1.0, 1.0),    # RGB（0-1）
    roughness=0.1,            # 0=镜面，1=哑光
    metallic=0.0,             # 0=介电质，1=金属
    opacity=1.0,              # 透明度
    emissive=(0.0, 0.0, 0.0), # 自发光
    ior=1.5,                  # 折射率
)
```

## 金属表面

```python
# 预定义金属
gs.surfaces.Iron()
gs.surfaces.Gold()
gs.surfaces.Copper()
gs.surfaces.Aluminium()

# 自定义金属
gs.surfaces.Metal(metal_type="gold", roughness=0.15)
```

## 透明表面

```python
# 玻璃
gs.surfaces.Glass(
    color=(0.9, 0.9, 1.0, 0.7),  # RGBA
    roughness=0.1,
    ior=1.5,
)

# 水
gs.surfaces.Water()
```

## 纹理

### 颜色纹理

```python
gs.textures.ColorTexture(color=(1.0, 0.0, 0.0))
```

### 图像纹理

```python
gs.textures.ImageTexture(
    image_path="textures/checker.png",
    encoding="srgb",  # 或 "linear" 用于非颜色数据
)
```

### 将纹理与表面结合使用

```python
surface = gs.surfaces.Rough(
    diffuse_texture=gs.textures.ImageTexture(image_path="albedo.png"),
    roughness_texture=gs.textures.ImageTexture(image_path="roughness.png", encoding="linear"),
    normal_texture=gs.textures.ImageTexture(image_path="normal.png", encoding="linear"),
)
```

## 可视化模式

```python
# 粒子可视化（用于流体）
gs.surfaces.Rough(color=(0.6, 0.8, 1.0), vis_mode="particle")

# 表面重建
gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7), vis_mode="recon")
```

## 环境贴图（光线追踪器）

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
