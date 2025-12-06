# `gs.surfaces.Collision`

`gs.surfaces.Collision` 是Genesis引擎中用于碰撞几何体的默认表面类型，主要用于物理碰撞检测和模拟，同时也提供了基本的视觉渲染能力。

## 主要功能

- 为碰撞几何体提供默认的灰色外观（默认颜色为 (0.5, 0.5, 0.5)）
- 支持基本的视觉属性调整（颜色、透明度、粗糙度等）
- 继承了Plastic类的所有功能，适用于各种碰撞场景
- 与物理引擎完全兼容，确保精确的碰撞检测
- 支持纹理贴图功能，可自定义碰撞体外观
- 提供双面渲染选项，适用于复杂碰撞几何体
- 支持法线贴图，增强碰撞体的视觉细节
- 可配置光束角度和法线差异限制，优化渲染效果

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | tuple | (0.5, 0.5, 0.5) | 表面颜色，采用RGB格式，值范围为 [0, 1] |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | Optional[float] | None | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞] |
| ior | Optional[float] | 1.0 | 折射率，用于计算透明和半透明材质的光学特性 |
| opacity_texture | Optional[Texture] | None | 不透明度纹理贴图，用于创建透明区域的图案 |
| roughness_texture | Optional[Texture] | None | 粗糙度纹理贴图，用于创建表面粗糙度的变化 |
| metallic_texture | Optional[Texture] | None | 金属度纹理贴图，用于创建金属和非金属区域的混合 |
| normal_texture | Optional[Texture] | None | 法线贴图，用于增强表面细节和立体感 |
| emissive_texture | Optional[Texture] | None | 自发光纹理贴图，用于创建发光区域的图案 |
| default_roughness | float | 1.0 | 默认粗糙度值，当roughness参数未设置时使用 |
| vis_mode | Optional[str] | None | 可视化模式，控制表面的渲染方式 |
| smooth | bool | True | 是否使用平滑着色，False表示使用平面着色 |
| double_sided | Optional[bool] | None | 是否双面渲染表面 |
| beam_angle | float | 180 | 光束角度，用于控制表面的光照效果 |
| normal_diff_clamp | float | 180 | 法线差异限制，用于优化渲染效果 |
| recon_backend | str | splashsurf | 重建后端，用于表面重建操作 |
| generate_foam | bool | False | 是否生成泡沫效果 |
| foam_options | Optional[FoamOptions] | None | 泡沫效果选项配置 |
| diffuse_texture | Optional[Texture] | None | 漫反射纹理贴图，用于控制表面的颜色和图案 |
| specular_texture | Optional[Texture] | None | 高光纹理贴图，用于控制表面的高光效果 |

## 使用示例

### 基本碰撞表面配置
```python
import genesis as gs

# 创建一个基本的碰撞表面
collision_surface = gs.surfaces.Collision(
    color=(0.8, 0.8, 0.8),  # 浅灰色
    opacity=1.0,            # 完全不透明
    roughness=0.5           # 中等粗糙度
)
```

### 半透明碰撞表面
```python
import genesis as gs

# 创建一个半透明的碰撞表面
collision_surface = gs.surfaces.Collision(
    color=(0.2, 0.6, 0.8),  # 蓝色
    opacity=0.5,            # 半透明
    smooth=True             # 平滑着色
)
```

### 使用纹理的碰撞表面
```python
import genesis as gs

# 创建一个带有纹理的碰撞表面
collision_surface = gs.surfaces.Collision(
    color=(1.0, 1.0, 1.0),  # 白色基础色
    roughness_texture=gs.textures.Texture(
        path="textures/roughness_map.png"
    ),
    normal_texture=gs.textures.Texture(
        path="textures/normal_map.png"
    )
)
```

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Collision
    :show-inheritance:
```
