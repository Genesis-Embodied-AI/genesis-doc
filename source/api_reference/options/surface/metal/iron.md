# `gs.surfaces.Iron`

`gs.surfaces.Iron` 是Genesis引擎中用于模拟铁金属材质的表面类型，是 `Metal` 表面的快捷方式，预配置了适合铁的参数值。

## 主要功能

- 模拟真实铁金属的光学特性和颜色表现（典型的银灰色）
- 默认设置 `metal_type = 'iron'`，无需手动指定
- 默认粗糙度为0.1，提供典型的铁表面光滑度
- 支持调整各种金属参数，如粗糙度、颜色等
- 与光线追踪渲染器完全兼容
- 支持各种纹理贴图，包括法线、粗糙度等

## 参数说明

该类继承了 `Metal` 类的所有参数，并将 `metal_type` 默认设置为 `'iron'`。有关详细参数说明，请参考 [Metal](./metal.md) 类的文档。

```{eval-rst}  
.. autoclass:: genesis.options.surfaces.Iron
```
