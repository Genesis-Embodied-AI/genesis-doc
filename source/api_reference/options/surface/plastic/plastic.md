# `gs.surfaces.Plastic`

## 概述

`gs.surfaces.Plastic` 是 `gs.surfaces.Surface` 类的子类，专门用于创建和配置塑料材质。它继承了 Surface 类的所有功能，并添加了塑料材质特有的漫反射纹理和高光纹理参数，使塑料材质的视觉效果更加真实。

## 主要功能

- **继承Surface类功能**：包括颜色、粗糙度、金属度等基本材质属性
- **漫反射纹理支持**：添加 diffuse_texture 用于精细控制塑料表面的漫反射特性
- **高光纹理支持**：添加 specular_texture 用于控制塑料表面的高光效果
- **灵活的参数控制**：支持调整透明度、折射率等光学参数
- **表面重建选项**：继承 Surface 类的表面重建配置

## 参数说明

Plastic 类继承了 Surface 类的所有参数，并添加了以下额外参数：

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `color` | `Optional[tuple]` | `None` | 表面颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `opacity` | `Optional[float]` | `None` | 表面透明度，取值范围 0.0（完全透明）到 1.0（完全不透明） |
| `roughness` | `Optional[float]` | `None` | 表面粗糙度，取值范围 0.0（完全光滑）到 1.0（完全粗糙） |
| `metallic` | `Optional[float]` | `None` | 金属度，通常设置为较低值（如 0.0）以模拟塑料特性 |
| `emissive` | `Optional[tuple]` | `None` | 发射光颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `ior` | `float` | `1.0` | 折射率，默认值为 1.0 |
| `opacity_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 透明度纹理 |
| `roughness_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 粗糙度纹理 |
| `metallic_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 金属度纹理 |
| `normal_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 法线纹理 |
| `emissive_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 发射光纹理 |
| `diffuse_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 漫反射纹理，控制塑料表面的漫反射特性 |
| `specular_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 高光纹理，控制塑料表面的高光效果 |
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
.. autoclass:: genesis.options.surfaces.Plastic
    :show-inheritance:
```
