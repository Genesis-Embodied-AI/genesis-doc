# `gs.renderers.RayTracer`

## 概述

`RayTracer` 是 Genesis 中的光线追踪渲染器类，它使用光线追踪技术来渲染场景。光线追踪渲染器可以产生非常真实的视觉效果，包括全局光照、反射、折射和阴影等，但通常比光栅化渲染器的性能要低。

## 主要功能

- 使用光线追踪技术进行高质量渲染
- 支持全局光照、反射、折射等高级视觉效果
- 提供多种采样和抗锯齿选项
- 支持材质和纹理渲染
- 适合需要高质量视觉效果的应用场景

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `samples_per_pixel` | int | 16 | 每像素的采样数量 |
| `max_bounces` | int | 8 | 光线的最大反弹次数 |
| `diffuse_samples` | int | 8 | 漫反射采样数量 |
| `specular_samples` | int | 8 | 镜面反射采样数量 |
| `transparency_samples` | int | 8 | 透明度采样数量 |
| `ambient_occlusion` | bool | True | 是否启用环境光遮蔽 |
| `ambient_occlusion_samples` | int | 4 | 环境光遮蔽采样数量 |
| `ambient_occlusion_distance` | float | 1.0 | 环境光遮蔽的距离 |
| `shadows` | bool | True | 是否启用阴影 |
| `shadow_samples` | int | 4 | 阴影采样数量 |
| `caustics` | bool | False | 是否启用焦散效果 |
| `caustics_samples` | int | 16 | 焦散效果采样数量 |
| `global_illumination` | bool | True | 是否启用全局光照 |
| `global_illumination_samples` | int | 8 | 全局光照采样数量 |
| `anti_aliasing` | bool | True | 是否启用抗锯齿 |
| `denoise` | bool | False | 是否启用去噪 |
| `denoise_strength` | float | 0.5 | 去噪强度 |
| `tone_mapping` | bool | True | 是否启用色调映射 |
| `tone_mapping_exposure` | float | 1.0 | 色调映射的曝光值 |
| `tone_mapping_gamma` | float | 2.2 | 色调映射的伽马值 |
| `wireframe` | bool | False | 是否启用线框模式 |
| `debug` | bool | False | 是否启用调试模式 |

```{eval-rst}  
.. autoclass:: genesis.options.renderers.RayTracer
```
