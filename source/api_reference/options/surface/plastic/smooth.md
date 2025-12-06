# `gs.surfaces.Smooth`

`gs.surfaces.Smooth` 是Genesis引擎中用于模拟光滑塑料表面的表面类型，是 `Plastic` 表面的快捷方式，预配置了适合光滑塑料的参数值。

## 主要功能

- 模拟光滑塑料材质的光学特性和外观
- 默认设置 `roughness = 0.1`，提供典型的光滑塑料表面效果
- 默认设置 `smooth = True`，启用平滑着色
- 默认折射率 `ior = 1.5`，适合大多数塑料材料
- 支持调整各种塑料参数，如颜色、透明度、粗糙度等
- 与光线追踪渲染器完全兼容
- 支持各种纹理贴图，包括颜色、粗糙度、法线等

## 参数说明

该类继承了 `Plastic` 类的所有参数，并将以下参数设置为特定的默认值：

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `roughness` | `float` | `0.1` | 表面粗糙度，设置为较低值以模拟光滑塑料 |
| `smooth` | `bool` | `True` | 启用平滑着色，提供更光滑的表面外观 |
| `ior` | `float` | `1.5` | 折射率，适合大多数塑料材料 |

有关完整参数说明，请参考 [Plastic](./plastic.md) 类的文档。

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Smooth
    :show-inheritance:
```
