# `gs.surfaces.Default`

## 概述

`gs.surfaces.Default` 是 Genesis 引擎中默认使用的表面材质类，实际上是 `gs.surfaces.Plastic` 类的别名，但添加了一些额外的透射参数。它提供了一个通用的材质配置，适用于大多数不需要特殊材质效果的场景。

## 主要功能

- **Plastic类的完全功能**：继承了 Plastic 类的所有功能和参数
- **额外透射参数**：添加了 specular_trans 和 diffuse_trans 参数用于控制透射效果
- **通用材质配置**：作为默认材质，提供了适用于大多数场景的合理默认值
- **完全兼容**：与 Plastic 类完全兼容，可以在任何使用 Plastic 的地方使用 Default

## 参数说明

Default 类继承了 Plastic 类的所有参数，并添加了以下额外参数：

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `color` | `Optional[tuple]` | `None` | 表面颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `opacity` | `Optional[float]` | `None` | 表面透明度，取值范围 0.0（完全透明）到 1.0（完全不透明） |
| `roughness` | `Optional[float]` | `None` | 表面粗糙度，取值范围 0.0（完全光滑）到 1.0（完全粗糙） |
| `metallic` | `Optional[float]` | `None` | 金属度，通常设置为较低值（如 0.0）以模拟塑料特性 |
| `emissive` | `Optional[tuple]` | `None` | 发射光颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `ior` | `Optional[float]` | `None` | 折射率 |
| `opacity_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 透明度纹理 |
| `roughness_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 粗糙度纹理 |
| `metallic_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 金属度纹理 |
| `normal_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 法线纹理 |
| `emissive_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 发射光纹理 |
| `diffuse_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 漫反射纹理 |
| `specular_trans` | `Optional[float]` | `0.0` | 镜面透射系数，控制镜面透射效果的强度 |
| `diffuse_trans` | `Optional[float]` | `0.0` | 漫反射透射系数，控制漫反射透射效果的强度 |
| `default_roughness` | `float` | `1.0` | 默认粗糙度值 |
| `vis_mode` | `Optional[str]` | `None` | 可视化模式 |
| `smooth` | `bool` | `True` | 是否启用平滑着色 |
| `double_sided` | `Optional[bool]` | `None` | 是否启用双面渲染 |
| `beam_angle` | `float` | `180` | 发射光的光束角度 |
| `normal_diff_clamp` | `float` | `180` | 计算表面法线时的阈值 |
| `recon_backend` | `str` | `splashsurf` | 表面重建后端，可选值：['splashsurf', 'openvdb'] |
| `generate_foam` | `bool` | `False` | 是否为基于粒子的实体生成泡沫效果 |
| `foam_options` | `Optional[genesis.options.misc.FoamOptions]` | `None` | 泡沫生成选项 |


```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Default
    :show-inheritance:
```
