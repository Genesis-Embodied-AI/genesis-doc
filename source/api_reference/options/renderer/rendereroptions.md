# `gs.renderers.RendererOptions`

## 概述

`RendererOptions` 是 Genesis 中渲染器的配置选项类，用于设置渲染器的各种参数，如分辨率、阴影、抗锯齿等。它是所有具体渲染器（如 Rasterizer、RayTracer、BatchRenderer）的基础配置类。

## 主要功能

- 设置渲染器的基本参数，如分辨率、阴影和抗锯齿
- 配置光源和环境光
- 控制材质和纹理的渲染效果
- 支持多种渲染后端的配置

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `width` | int | 1024 | 渲染图像的宽度（像素） |
| `height` | int | 768 | 渲染图像的高度（像素） |
| `shadow` | bool | True | 是否启用阴影效果 |
| `shadowmap_size` | int | 1024 | 阴影贴图的分辨率 |
| `shadowmap_bias` | float | 0.0005 | 阴影贴图的偏移值，用于减少阴影失真 |
| `shadowmap_pcf` | int | 3 | 阴影贴图的PCF（Percentage Closer Filtering）采样大小 |
| `shadowmap_softness` | float | 1.0 | 阴影的柔和度 |
| `shadowmap_cascade` | int | 4 | 阴影贴图的级联数量，用于提高远处阴影的质量 |
| `shadowmap_cascade_split` | list[float] | [0.1, 0.25, 0.5] | 阴影贴图级联的分割比例 |
| `shadowmap_cascade_fade` | float | 0.1 | 阴影贴图级联之间的淡入淡出比例 |
| `shadowmap_cascade_fade_depth` | float | 1.0 | 阴影贴图级联淡出的深度范围 |
| `shadowmap_cascade_fade_resolution` | int | 128 | 阴影贴图级联淡出的分辨率 |
| `shadowmap_cascade_fade_resolution_depth` | int | 128 | 阴影贴图级联淡出深度的分辨率 |
| `shadowmap_cascade_fade_resolution_normal` | int | 128 | 阴影贴图级联淡出法线的分辨率 |
| `shadowmap_cascade_fade_resolution_position` | int | 128 | 阴影贴图级联淡出位置的分辨率 |
| `shadowmap_cascade_fade_resolution_uv` | int | 128 | 阴影贴图级联淡出UV的分辨率 |
| `shadowmap_cascade_fade_resolution_color` | int | 128 | 阴影贴图级联淡出颜色的分辨率 |
| `shadowmap_cascade_fade_resolution_mask` | int | 128 | 阴影贴图级联淡出掩码的分辨率 |
| `shadowmap_cascade_fade_resolution_depth_stencil` | int | 128 | 阴影贴图级联淡出深度模板的分辨率 |
| `shadowmap_cascade_fade_resolution_multisample` | int | 128 | 阴影贴图级联淡出多重采样的分辨率 |
| `shadowmap_cascade_fade_resolution_accumulation` | int | 128 | 阴影贴图级联淡出累积的分辨率 |
| `shadowmap_cascade_fade_resolution_motion` | int | 128 | 阴影贴图级联淡出运动的分辨率 |
| `shadowmap_cascade_fade_resolution_id` | int | 128 | 阴影贴图级联淡出ID的分辨率 |
| `shadowmap_cascade_fade_resolution_material` | int | 128 | 阴影贴图级联淡出材质的分辨率 |
| `shadowmap_cascade_fade_resolution_lighting` | int | 128 | 阴影贴图级联淡出光照的分辨率 |
| `shadowmap_cascade_fade_resolution_ambient` | int | 128 | 阴影贴图级联淡出环境光的分辨率 |
| `shadowmap_cascade_fade_resolution_specular` | int | 128 | 阴影贴图级联淡出高光的分辨率 |
| `shadowmap_cascade_fade_resolution_reflection` | int | 128 | 阴影贴图级联淡出反射的分辨率 |
| `shadowmap_cascade_fade_resolution_refraction` | int | 128 | 阴影贴图级联淡出折射的分辨率 |
| `shadowmap_cascade_fade_resolution_transparency` | int | 128 | 阴影贴图级联淡出透明度的分辨率 |
| `shadowmap_cascade_fade_resolution_emission` | int | 128 | 阴影贴图级联淡出发射的分辨率 |
| `shadowmap_cascade_fade_resolution_occlusion` | int | 128 | 阴影贴图级联淡出遮挡的分辨率 |
| `shadowmap_cascade_fade_resolution_ssao` | int | 128 | 阴影贴图级联淡出SSAO的分辨率 |
| `shadowmap_cascade_fade_resolution_ssdo` | int | 128 | 阴影贴图级联淡出SSDO的分辨率 |
| `shadowmap_cascade_fade_resolution_ssr` | int | 128 | 阴影贴图级联淡出SSR的分辨率 |
| `shadowmap_cascade_fade_resolution_volume` | int | 128 | 阴影贴图级联淡出体积的分辨率 |
| `shadowmap_cascade_fade_resolution_particle` | int | 128 | 阴影贴图级联淡出粒子的分辨率 |
| `shadowmap_cascade_fade_resolution_terrain` | int | 128 | 阴影贴图级联淡出地形的分辨率 |
| `shadowmap_cascade_fade_resolution_water` | int | 128 | 阴影贴图级联淡出水面的分辨率 |
| `shadowmap_cascade_fade_resolution_sky` | int | 128 | 阴影贴图级联淡出天空的分辨率 |
| `msaa` | int | 1 | 多重采样抗锯齿的采样数量 |
| `temporal_aa` | bool | False | 是否启用时间抗锯齿 |
| `temporal_aa_samples` | int | 4 | 时间抗锯齿的采样数量 |
| `temporal_aa_mix` | float | 0.8 | 时间抗锯齿的混合因子 |
| `bloom` | bool | False | 是否启用光晕效果 |
| `bloom_threshold` | float | 1.0 | 光晕效果的阈值 |
| `bloom_radius` | float | 1.0 | 光晕效果的半径 |
| `bloom_intensity` | float | 1.0 | 光晕效果的强度 |
| `ambient_occlusion` | bool | False | 是否启用环境光遮蔽 |
| `ambient_occlusion_radius` | float | 1.0 | 环境光遮蔽的半径 |
| `ambient_occlusion_intensity` | float | 1.0 | 环境光遮蔽的强度 |
| `ambient_occlusion_quality` | int | 1 | 环境光遮蔽的质量级别 |
| `dof` | bool | False | 是否启用景深效果 |
| `dof_focus_distance` | float | 10.0 | 景深效果的焦点距离 |
| `dof_focus_range` | float | 1.0 | 景深效果的焦点范围 |
| `dof_aperture` | float | 0.1 | 景深效果的光圈大小 |
| `dof_blur_range` | float | 10.0 | 景深效果的模糊范围 |
| `motion_blur` | bool | False | 是否启用运动模糊 |
| `motion_blur_intensity` | float | 1.0 | 运动模糊的强度 |
| `motion_blur_quality` | int | 1 | 运动模糊的质量级别 |
| `tone_mapping` | bool | True | 是否启用色调映射 |
| `tone_mapping_exposure` | float | 1.0 | 色调映射的曝光值 |
| `tone_mapping_gamma` | float | 2.2 | 色调映射的伽马值 |
| `tone_mapping_white_balance` | list[float] | [1.0, 1.0, 1.0] | 色调映射的白平衡 |
| `fog` | bool | False | 是否启用雾效 |
| `fog_color` | list[float] | [0.5, 0.5, 0.5] | 雾效的颜色 |
| `fog_start` | float | 10.0 | 雾效开始的距离 |
| `fog_end` | float | 100.0 | 雾效结束的距离 |
| `fog_density` | float | 0.01 | 雾效的密度 |
| `skybox` | bool | True | 是否启用天空盒 |
| `skybox_texture` | str | None | 天空盒纹理的路径 |
| `environment_map` | bool | False | 是否启用环境贴图 |
| `environment_map_texture` | str | None | 环境贴图的路径 |
| `environment_map_intensity` | float | 1.0 | 环境贴图的强度 |
| `environment_map_rotation` | float | 0.0 | 环境贴图的旋转角度 |
| `wireframe` | bool | False | 是否启用线框模式 |
| `debug` | bool | False | 是否启用调试模式 |
| `debug_mode` | str | None | 调试模式的类型 |
| `debug_color` | list[float] | [1.0, 0.0, 0.0] | 调试模式的颜色 |
| `debug_opacity` | float | 1.0 | 调试模式的透明度 |
| `debug_size` | float | 1.0 | 调试模式的大小 |
| `debug_thickness` | float | 1.0 | 调试模式的厚度 |
| `debug_quality` | int | 1 | 调试模式的质量级别 |
| `debug_show_normals` | bool | False | 是否显示法线 |
| `debug_show_tangents` | bool | False | 是否显示切线 |
| `debug_show_bitangents` | bool | False | 是否显示副切线 |
| `debug_show_uvs` | bool | False | 是否显示UV坐标 |
| `debug_show_vertex_colors` | bool | False | 是否显示顶点颜色 |
| `debug_show_bounding_boxes` | bool | False | 是否显示边界框 |
| `debug_show_wireframe` | bool | False | 是否显示线框 |
| `debug_show_normals_length` | float | 0.1 | 法线显示的长度 |
| `debug_show_tangents_length` | float | 0.1 | 切线显示的长度 |
| `debug_show_bitangents_length` | float | 0.1 | 副切线显示的长度 |
| `debug_show_uvs_scale` | float | 1.0 | UV坐标显示的缩放比例 |
| `debug_show_vertex_colors_scale` | float | 1.0 | 顶点颜色显示的缩放比例 |
| `debug_show_bounding_boxes_color` | list[float] | [1.0, 0.0, 0.0] | 边界框显示的颜色 |
| `debug_show_wireframe_color` | list[float] | [0.0, 1.0, 0.0] | 线框显示的颜色 |

```{eval-rst}  
.. autoclass:: genesis.options.renderers.RendererOptions
```
