# `gs.surfaces.Emission`

`gs.surfaces.Emission` 是Genesis引擎中的自发光表面类型，主要用于创建能够自身发光的物体。在Genesis的光线追踪管道中，光源不是特殊类型的对象，而是带有自发光表面的实体。

## 主要功能

- 允许物体自身发光，用于创建各种光源效果
- 支持自定义发光颜色和强度
- 可以使用纹理贴图定义发光区域和图案
- 继承了基础表面的所有属性（颜色、透明度、粗糙度等）
- 适用于创建霓虹灯、指示灯、发光标志等效果
- 支持双面发光效果
- 可与其他材质属性结合使用，创建复杂的视觉效果

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|--------|------|
| color | Optional[tuple] | None | 表面颜色，采用RGB格式，值范围为 [0, 1] |
| opacity | Optional[float] | None | 表面不透明度，值范围为 [0, 1]，0表示完全透明，1表示完全不透明 |
| roughness | Optional[float] | None | 表面粗糙度，值范围为 [0, 1]，0表示完全光滑，1表示完全粗糙 |
| metallic | Optional[float] | None | 金属度，值范围为 [0, 1]，0表示非金属，1表示金属 |
| emissive | Optional[tuple] | None | 自发光颜色，采用RGB格式，值范围为 [0, ∞]，值越大发光越强 |
| ior | Optional[float] | None | 折射率，用于计算透明和半透明材质的光学特性 |
| opacity_texture | Optional[Texture] | None | 不透明度纹理贴图 |
| roughness_texture | Optional[Texture] | None | 粗糙度纹理贴图 |
| metallic_texture | Optional[Texture] | None | 金属度纹理贴图 |
| normal_texture | Optional[Texture] | None | 法线贴图 |
| emissive_texture | Optional[Texture] | None | 自发光纹理贴图，用于定义发光区域和图案 |
| default_roughness | float | 1.0 | 默认粗糙度值，当roughness参数未设置时使用 |
| vis_mode | Optional[str] | None | 可视化模式，控制表面的渲染方式 |
| smooth | bool | True | 是否使用平滑着色，False表示使用平面着色 |
| double_sided | Optional[bool] | None | 是否双面渲染表面 |
| beam_angle | float | 180 | 光束角度，用于控制表面的光照效果 |
| normal_diff_clamp | float | 180 | 法线差异限制，用于优化渲染效果 |
| recon_backend | str | splashsurf | 重建后端，用于表面重建操作 |
| generate_foam | bool | False | 是否生成泡沫效果 |
| foam_options | Optional[FoamOptions] | None | 泡沫效果选项配置 |

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Emission
```
