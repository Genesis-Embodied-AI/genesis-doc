# `gs.options.ViewerOptions`

`ViewerOptions` 是 Genesis API 中用于配置场景查看器行为和相机参数的类，允许用户自定义查看器的窗口大小、渲染性能和相机设置。

## 主要功能

- 配置查看器窗口的分辨率和显示属性
- 控制查看器的运行模式（主线程或后台线程）
- 设置渲染刷新率和 FPS 限制
- 自定义相机的位置、朝向和视场角
- 控制查看器的交互行为

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| res | `Optional[tuple]` | `None` | 查看器窗口的分辨率，格式为 (宽度, 高度) |
| run_in_thread | `Optional[bool]` | `None` | 是否在后台线程运行查看器（在 MacOS 上不支持） |
| refresh_rate | `int` | `60` | 查看器的刷新率（帧/秒） |
| max_FPS | `Optional[int]` | `60` | 查看器的最大 FPS 限制，会同步仿真速度 |
| camera_pos | `tuple` | `(3.5, 0.5, 2.5)` | 相机的位置坐标 (x, y, z) |
| camera_lookat | `tuple` | `(0.0, 0.0, 0.5)` | 相机的注视点坐标 (x, y, z) |
| camera_up | `tuple` | `(0.0, 0.0, 1.0)` | 相机的上向量 (x, y, z) |
| camera_fov | `float` | `40` | 相机的视场角（度数） |
| enable_interaction | `bool` | `False` | 是否启用查看器交互功能 |

```{eval-rst}  
.. autoclass:: genesis.options.ViewerOptions
    :show-inheritance:
```
