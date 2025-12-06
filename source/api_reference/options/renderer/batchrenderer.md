# `gs.renderers.BatchRenderer`

## 概述

`BatchRenderer` 是 Genesis 中的批量渲染器类，它允许一次性渲染多个场景或视角，提高渲染效率。批量渲染器适合需要生成大量图像或动画的应用场景，如批量生成训练数据、动画渲染等。

## 主要功能

- 支持批量渲染多个场景或视角
- 提供多种渲染模式和选项
- 支持多线程渲染，提高渲染效率
- 支持材质和纹理渲染
- 适合需要生成大量图像或动画的应用场景

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| `renderer` | object | None | 使用的渲染器实例，可以是 Rasterizer 或 RayTracer |
| `num_threads` | int | 4 | 用于渲染的线程数量 |
| `output_format` | str | "png" | 输出图像的格式，可以是 "png"、"jpg"、"exr" 或 "tiff" |
| `output_path` | str | "./output" | 输出图像的路径 |
| `file_prefix` | str | "render" | 输出文件名的前缀 |
| `file_suffix` | str | "" | 输出文件名的后缀 |
| `start_frame` | int | 0 | 开始渲染的帧编号 |
| `end_frame` | int | 100 | 结束渲染的帧编号 |
| `step_frame` | int | 1 | 渲染的帧步长 |
| `save_depth` | bool | False | 是否保存深度图 |
| `save_normals` | bool | False | 是否保存法线图 |
| `save_albedo` | bool | False | 是否保存反照率图 |
| `save_material` | bool | False | 是否保存材质图 |
| `save_id` | bool | False | 是否保存ID图 |
| `save_mask` | bool | False | 是否保存掩码图 |
| `wireframe` | bool | False | 是否启用线框模式 |
| `debug` | bool | False | 是否启用调试模式 |

```{eval-rst}  
.. autoclass:: genesis.options.renderers.BatchRenderer
```
