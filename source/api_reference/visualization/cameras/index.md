# 相机（Cameras）

Genesis 中的相机是从仿真中捕获视觉信息的传感器。它们可以渲染 RGB 图像、深度图、分割掩码和其他视觉数据。

## 概述

Genesis 提供了一个统一的 `Camera` 类，可与不同的渲染后端配合使用：

- **Rasterizer 相机**：快速渲染，适用于实时使用
- **Raytracer 相机**：照片级真实感渲染
- **BatchRenderer 相机**：高吞吐量的并行渲染

## 添加相机

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.build()

# 添加相机
cam = scene.add_camera(
    res=(1280, 720),       # 分辨率（宽，高）
    pos=(3, 0, 2),         # 相机位置
    lookat=(0, 0, 0.5),    # 目标点
    fov=40,                # 视野角度（度）
    up=(0, 0, 1),          # 向上向量
)
```

## 渲染图像

```python
# 执行仿真步骤
scene.step()

# 渲染不同类型的输出
rgb = cam.render(rgb=True)                    # RGB 图像
depth = cam.render(depth=True)                # 深度图
segmentation = cam.render(segmentation=True)  # 分割
normal = cam.render(normal=True)              # 表面法线

# 同时渲染多种类型
outputs = cam.render(rgb=True, depth=True)
```

## 相机参数

| 参数 | 类型 | 描述 |
|-----------|------|-------------|
| `res` | tuple (W, H) | 图像分辨率 |
| `pos` | tuple (x, y, z) | 相机位置 |
| `lookat` | tuple (x, y, z) | 相机注视点 |
| `up` | tuple (x, y, z) | 向上方向 |
| `fov` | float | 垂直视野角度（度） |
| `model` | str | 相机模型：`pinhole` 或 `thinlens` |
| `spp` | int | 每像素采样数（仅 raytracer） |
| `denoise` | bool | 启用降噪（仅 raytracer） |

## 相机模型

### Pinhole 相机（默认）

具有无限景深的标准透视相机：

```python
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="pinhole",
)
```

### Thin Lens 相机

具有景深的基于物理的相机：

```python
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="thinlens",
    aperture=0.1,       # 光圈大小
    focus_dist=3.0,     # 对焦距离
)
```

## 动态相机控制

```python
# 在仿真过程中更新相机位置
cam.set_pose(
    pos=(5, 0, 3),
    lookat=(0, 0, 0),
)

# 跟随实体
cam.follow_entity(robot, offset=(2, 0, 1))
```

## 组件

```{toctree}
:titlesonly:

camera
```

## 另请参阅

- {doc}`/api_reference/visualization/renderers/index` - 渲染后端
- {doc}`/api_reference/sensor/index` - 其他传感器类型
