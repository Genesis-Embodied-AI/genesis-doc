# `gs.surfaces.Water`

`gs.surfaces.Water` 是Genesis引擎中用于模拟水面材质的表面类型，是 `Glass` 表面的快捷方式，预配置了适合模拟水的参数值。

## 主要功能

- 预配置的水材质，使用适合水的参数值
- 默认颜色为蓝绿色 (0.61, 0.98, 0.93)，模拟自然水面
- 默认粗糙度为0.2，模拟水面的轻微波动
- 默认折射率为1.2，符合水的光学特性
- 支持透明度调整，可创建清澈或浑浊的水面效果
- 支持纹理贴图，可添加波纹、泡沫等细节
- 支持生成泡沫效果，增强水面真实感
- 与流体模拟系统兼容，可用于动态水面

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | tuple | (0.61, 0.98, 0.93) | 表面颜色，采用RGB格式，默认值为蓝绿色 |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | float | 0.2 | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞] |
| ior | float | 1.2 | 折射率，用于计算光的折射效果（水的折射率约为1.333，这里使用1.2作为模拟值） |
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
| thickness | Optional[float] | None | 水体厚度，用于模拟真实水体的厚度效果 |
| thickness_texture | Optional[Texture] | None | 厚度纹理贴图 |
| specular_texture | Optional[Texture] | None | 高光纹理贴图 |
| transmission_texture | Optional[Texture] | None | 透射纹理贴图 |

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Water
```
