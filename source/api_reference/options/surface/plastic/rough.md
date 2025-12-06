# `gs.surfaces.Rough`

## 概述

`gs.surfaces.Rough` 是 Genesis 引擎中用于创建粗糙塑料表面的快捷类。它继承自 `gs.surfaces.Plastic` 类，并将粗糙度 (`roughness`) 默认设置为 1.0（完全粗糙），折射率 (`ior`) 默认设置为 1.5，适合模拟砂纸、粗布等粗糙表面效果。

## 主要功能

- **继承Plastic类功能**：包括颜色、透明度、纹理支持等塑料材质的所有特性
- **默认高粗糙度**：粗糙度默认值为 1.0，无需手动设置即可获得完全粗糙的表面效果
- **优化的折射率**：折射率默认值为 1.5，提供更真实的光学效果
- **快速配置**：作为快捷类，可在不指定额外参数的情况下创建粗糙塑料材质

## 参数说明

Rough 类继承了 Plastic 类的所有参数，但对以下参数设置了特定的默认值：

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `color` | `Optional[tuple]` | `None` | 表面颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `opacity` | `Optional[float]` | `None` | 表面透明度，取值范围 0.0（完全透明）到 1.0（完全不透明） |
| `roughness` | `float` | `1.0` | 表面粗糙度，固定为完全粗糙 |
| `metallic` | `Optional[float]` | `None` | 金属度，通常设置为较低值（如 0.0）以模拟塑料特性 |
| `emissive` | `Optional[tuple]` | `None` | 发射光颜色，格式为 (R, G, B)，取值范围 0.0-1.0 |
| `ior` | `float` | `1.5` | 折射率，默认值为 1.5 |
| `opacity_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 透明度纹理 |
| `roughness_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 粗糙度纹理 |
| `metallic_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 金属度纹理 |
| `normal_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 法线纹理 |
| `emissive_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 发射光纹理 |
| `diffuse_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 漫反射纹理 |
| `specular_texture` | `Optional[genesis.options.textures.Texture]` | `None` | 高光纹理 |
| `default_roughness` | `float` | `1.0` | 默认粗糙度值 |
| `vis_mode` | `Optional[str]` | `None` | 可视化模式 |
| `smooth` | `bool` | `True` | 是否启用平滑着色 |
| `double_sided` | `Optional[bool]` | `None` | 是否启用双面渲染 |

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Rough
    :show-inheritance:
```
