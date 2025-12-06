# `gs.renderers.Rasterizer`

## 概述

`Rasterizer` 是 Genesis 中的光栅化渲染器类，它使用传统的光栅化技术来渲染场景。光栅化渲染器具有较高的性能，适合实时渲染场景，但在某些视觉效果上（如全局光照、反射等）可能不如光线追踪渲染器。

## 主要功能

- 使用光栅化技术进行实时渲染
- 支持阴影、抗锯齿和基本的后处理效果
- 提供多种渲染模式和选项
- 支持材质和纹理渲染
- 适合需要高性能的实时应用场景

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `vis_mode` | str | "default" | 可视化模式，可以是 "default"、"wireframe"、"normals"、"uv"、"vertex_color" 或 "material" |
| `smooth` | bool | True | 是否启用平滑着色 |
| `double_sided` | bool | False | 是否启用双面渲染 |
| `shadows` | bool | True | 是否启用阴影 |
| `shadowmap_size` | int | 1024 | 阴影贴图的分辨率 |
| `msaa_samples` | int | 1 | 多重采样抗锯齿的采样数量 |
| `temporal_aa` | bool | False | 是否启用时间抗锯齿 |
| `bloom` | bool | False | 是否启用光晕效果 |
| `bloom_threshold` | float | 1.0 | 光晕效果的阈值 |
| `bloom_radius` | float | 1.0 | 光晕效果的半径 |
| `bloom_intensity` | float | 1.0 | 光晕效果的强度 |
| `ambient_occlusion` | bool | False | 是否启用环境光遮蔽 |
| `ambient_occlusion_radius` | float | 0.5 | 环境光遮蔽的半径 |
| `ambient_occlusion_intensity` | float | 1.0 | 环境光遮蔽的强度 |
| `tone_mapping` | bool | True | 是否启用色调映射 |
| `tone_mapping_exposure` | float | 1.0 | 色调映射的曝光值 |
| `wireframe` | bool | False | 是否启用线框模式 |
| `debug` | bool | False | 是否启用调试模式 |

```{eval-rst}  
.. autoclass:: genesis.options.renderers.Rasterizer
```
