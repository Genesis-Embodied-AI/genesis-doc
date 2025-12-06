# `gs.textures.ImageTexture`

## 概述

`gs.textures.ImageTexture` 是 `gs.textures.Texture` 类的子类，用于创建基于图像的纹理。它允许用户通过图像文件或图像数组为材质添加复杂的颜色变化和细节，是创建真实感材质的重要工具。ImageTexture 支持多种图像格式和编码方式，可应用于材质的各种属性。

## 主要功能

- **基于图像的纹理**：支持通过图像文件或图像数组创建纹理
- **灵活的图像源**：可从文件路径或 NumPy 数组加载图像
- **图像编码控制**：支持 sRGB 和线性编码方式
- **颜色调整**：可通过 image_color 参数调整图像颜色强度
- **高质量渲染**：支持高分辨率图像和各种图像格式
- **与材质系统集成**：可作为各种材质属性的纹理使用

## 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `image_path` | `Optional[str]` | `None` | 图像文件路径 |
| `image_array` | `Optional[numpy.ndarray]` | `None` | 图像数组（NumPy 格式） |
| `image_color` | `Union[float, List[float], None]` | `None` | 图像颜色因子，与图像颜色相乘，可用于调整图像亮度或颜色 |
| `encoding` | `str` | `'srgb'` | 图像编码方式。可选值：
  - `'srgb'`: RGB 图像的标准编码方式
  - `'linear'`: 通用图像（如透明度、粗糙度、法线贴图等）的编码方式 |

## 使用示例

```{eval-rst}  
.. autoclass:: genesis.options.textures.ImageTexture
    :show-inheritance:
```
