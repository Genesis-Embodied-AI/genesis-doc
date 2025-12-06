# `gs.textures.ColorTexture`

## 概述

`gs.textures.ColorTexture` 是 `gs.textures.Texture` 类的子类，用于创建单一颜色的纹理。它是 Genesis 引擎中最基本的纹理类型之一，通过设置单一颜色值来为材质添加均匀的颜色效果。ColorTexture 可以作为材质的颜色属性使用，也可以与其他纹理类型结合应用。

## 主要功能

- **单一颜色纹理**：创建具有均匀颜色的纹理
- **灵活的颜色设置**：支持使用浮点数（灰度）或 RGB 元组设置颜色
- **与材质系统集成**：可作为各种材质的颜色纹理使用
- **简洁的 API**：使用简单直观的接口创建颜色纹理
- **高质量渲染**：支持精确的颜色控制和渲染

## 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `color` | `Union[float, List[float]]` | `(1.0, 1.0, 1.0)` | 纹理颜色。可以是单个浮点数（表示灰度值，范围 0.0-1.0）或 RGB 元组（范围 0.0-1.0） |

```{eval-rst}  
.. autoclass:: genesis.options.textures.ColorTexture
    :show-inheritance:
```
