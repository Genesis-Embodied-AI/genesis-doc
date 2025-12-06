# `Camera`

`Camera` 是 Genesis 引擎中用于模拟相机的类，用于获取场景的视觉信息，支持多种相机参数和渲染选项。

## 功能说明

- 控制相机的位置、姿态和视角参数
- 支持透视投影和正交投影
- 提供场景渲染功能，包括 RGB 图像、深度图、分割图等
- 支持相机跟随实体运动
- 支持录制视频

## 主要属性

| 属性名 | 类型 | 描述 |
| ------ | ---- | ---- |
| `idx` | int | 相机索引 |
| `uid` | int | 相机唯一标识符 |
| `pos` | list | 相机位置 |
| `lookat` | list | 相机看向的点 |
| `up` | list | 相机上方向向量 |
| `fov` | float | 视场角（度） |
| `focal_len` | float | 焦距 |
| `aspect_ratio` | float | 宽高比 |
| `near` | float | 近裁剪面 |
| `far` | float | 远裁剪面 |
| `res` | list | 分辨率 [宽度, 高度] |
| `extrinsics` | list | 相机外参矩阵 |
| `intrinsics` | list | 相机内参矩阵 |
| `transform` | list | 相机变换矩阵 |

```{eval-rst}  
.. automodule:: genesis.vis.camera
    :members:
    :show-inheritance:
    :undoc-members:
```
