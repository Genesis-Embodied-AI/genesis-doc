# `gs.surfaces.Surface`

## 概述

`gs.surfaces.Surface` 是 Genesis 引擎中用于定义和控制实体表面属性的核心类。它允许用户配置材料的视觉外观（如颜色、粗糙度、金属度）、光学特性（如折射率、发射光）以及表面重建和渲染选项。

## 主要功能

- **视觉属性配置**：设置颜色、粗糙度、金属度等基本材质属性
- **纹理支持**：支持多种纹理类型（透明度、粗糙度、金属度、法线、发射光）
- **光学特性**：控制折射率、透明度等光学参数
- **表面重建**：配置表面重建后端（splashsurf 或 openvdb）
- **发射光效果**：设置发光颜色和光束角度
- **双面渲染**：支持双面渲染选项
- **泡沫生成**：为基于粒子的实体启用泡沫生成效果
- **平滑着色**：控制表面平滑着色选项

## 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `color` | `Optional[tuple]` | `None` | 表面颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `opacity` | `Optional[float]` | `None` | 表面透明度，取值范围 0.0（完全透明）到 1.0（完全不透明） |
| `roughness` | `Optional[float]` | `None` | 表面粗糙度，取值范围 0.0（完全光滑）到 1.0（完全粗糙） |
| `metallic` | `Optional[float]` | `None` | 金属度，取值范围 0.0（非金属）到 1.0（金属） |
| `emissive` | `Optional[tuple]` | `None` | 发射光颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `ior` | `Optional[float]` | `None` | 折射率，影响光在介质中的传播 |
| `opacity_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 透明度纹理 |
| `roughness_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 粗糙度纹理 |
| `metallic_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 金属度纹理 |
| `normal_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 法线纹理 |
| `emissive_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 发射光纹理 |
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
.. autoclass:: genesis.options.surfaces.Surface
```
