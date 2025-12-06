# `gs.surfaces.Reflective`

`gs.surfaces.Reflective` 是Genesis引擎中一种高反射性塑料表面的快捷方式，比 `Smooth` 表面更加光滑，主要用于创建具有强烈镜面反射效果的材质。

## 主要功能

- 提供高反射性的塑料材质，默认粗糙度极低（0.01）
- 设置了较高的折射率（2.0），增强反射效果
- 继承了Plastic类的所有功能，支持各种视觉属性调整
- 适用于创建类似镜面的反射表面
- 支持纹理贴图功能，可自定义反射表面外观
- 提供双面渲染选项，适用于复杂几何体
- 支持法线贴图，增强表面细节
- 与物理引擎兼容，可用于碰撞检测

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | Optional[tuple] | None | 表面颜色，采用RGB格式，值范围为 [0, 1] |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | float | 0.01 | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞] |
| ior | float | 2.0 | 折射率，用于计算透明和半透明材质的光学特性 |
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

### 基本反射表面配置
```python
import genesis as gs

# 创建一个基本的反射表面
reflective_surface = gs.surfaces.Reflective(
    color=(0.9, 0.9, 0.9),  # 白色
    opacity=1.0             # 完全不透明
)
```

### 彩色反射表面
```python
import genesis as gs

# 创建一个彩色的反射表面
reflective_surface = gs.surfaces.Reflective(
    color=(0.2, 0.3, 0.8),  # 蓝色
    ior=1.5                 # 调整折射率
)
```

### 半透明反射表面
```python
import genesis as gs

# 创建一个半透明的反射表面
reflective_surface = gs.surfaces.Reflective(
    color=(1.0, 0.8, 0.2),  # 黄色
    opacity=0.8,            # 半透明
    roughness=0.05          # 略微增加粗糙度
)
```

### 使用纹理的反射表面
```python
import genesis as gs

# 创建一个带有纹理的反射表面
reflective_surface = gs.surfaces.Reflective(
    color=(1.0, 1.0, 1.0),  # 白色基础色
    specular_texture=gs.textures.Texture(
        path="textures/specular_map.png"
    ),
    normal_texture=gs.textures.Texture(
        path="textures/normal_map.png"
    )
)
```

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Reflective
    :show-inheritance:
```
