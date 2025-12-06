# `gs.surfaces.Metal`

`gs.surfaces.Metal` 是Genesis引擎中用于模拟金属材质的表面类型，支持真实的金属反射特性和高光效果，适用于创建各种金属物体。

## 主要功能

- 模拟真实金属的光学特性，包括高反射率和特定的颜色表现
- 默认粗糙度为0.1，提供典型的金属表面光滑度
- 支持自定义金属类型，包括铁、铝、铜和金
- 默认金属类型为铁（iron）
- 支持调整金属度参数，控制金属特性的强度
- 支持各种纹理贴图，包括法线、粗糙度、金属度等
- 与光线追踪渲染器完全兼容，提供真实的光影效果
- 可用于创建从粗糙到抛光的各种金属表面效果

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | Optional[tuple] | None | 表面颜色，采用RGB格式，值范围为 [0, 1] |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | Optional[float] | 0.1 | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞] |
| ior | Optional[float] | None | 折射率，用于计算光的折射效果 |
| opacity_texture | Optional[Texture] | None | 不透明度纹理贴图 |
| roughness_texture | Optional[Texture] | None | 粗糙度纹理贴图 |
| metallic_texture | Optional[Texture] | None | 金属度纹理贴图 |
| normal_texture | Optional[Texture] | None | 法线贴图，用于增强表面细节 |
| emissive_texture | Optional[Texture] | None | 自发光纹理贴图 |
| default_roughness | float | 1.0 | 默认粗糙度值，当roughness参数未设置时使用 |
| vis_mode | Optional[str] | None | 可视化模式，控制表面的渲染方式 |
| smooth | bool | True | 是否使用平滑着色，False表示使用平面着色 |
| double_sided | Optional[bool] | None | 是否双面渲染表面 |
| beam_angle | float | 180 | 光束角度，用于控制表面的光照效果 |
| normal_diff_clamp | float | 180 | 法线差异限制，用于优化渲染效果 |
| recon_backend | str | splashsurf | 重建后端，用于表面重建操作 |
| generate_foam | bool | False | 是否生成泡沫效果 |
| foam_options | Optional[FoamOptions] | None | 泡沫效果选项配置 |
| metal_type | Optional[str] | iron | 金属类型，可选值为 iron, aluminium, copper, gold |
| diffuse_texture | Optional[Texture] | None | 漫反射纹理贴图 |

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Metal
```
