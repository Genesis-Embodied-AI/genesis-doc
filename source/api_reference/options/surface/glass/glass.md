# `gs.surfaces.Glass`

`gs.surfaces.Glass` 是Genesis引擎中用于模拟玻璃材质的表面类型，支持真实的光折射和反射效果，适用于创建各种透明和半透明的物体。

## 主要功能

- 模拟真实玻璃的光学特性，包括折射和反射
- 默认粗糙度为0.0，提供极高的表面光滑度
- 默认折射率为1.5，模拟普通玻璃的光学特性
- 支持透明度调整，可创建半透明效果
- 支持次表面散射效果，增强真实感
- 支持厚度参数，用于模拟不同厚度的玻璃
- 提供多种纹理贴图选项，包括透明度、法线、厚度等
- 与光线追踪渲染器完全兼容

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | Optional[tuple] | None | 表面颜色，采用RGB格式，值范围为 [0, 1] |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | float | 0.0 | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞] |
| ior | float | 1.5 | 折射率，用于计算光的折射效果（普通玻璃的折射率约为1.5） |
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
| subsurface | bool | False | 是否开启次表面散射效果 |
| thickness | Optional[float] | None | 玻璃厚度，用于模拟真实玻璃的厚度效果 |
| thickness_texture | Optional[Texture] | None | 厚度纹理贴图 |
| specular_texture | Optional[Texture] | None | 高光纹理贴图 |
| transmission_texture | Optional[Texture] | None | 透射纹理贴图 |

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Glass
```
