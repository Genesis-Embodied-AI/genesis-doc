# Visualizer

`Visualizer` 类是 Genesis 中所有可视化和渲染的主控制器。它管理 viewer、相机和渲染器后端。

## 概述

当你创建 `Scene` 时，Visualizer 会自动创建，并负责：

- 管理交互式 `Viewer` 窗口
- 协调多个 `Camera` 实例
- 处理渲染器后端（Rasterizer、Raytracer、BatchRenderer）
- 将渲染状态与仿真同步

## 访问方式

通过 scene 访问 Visualizer：

```python
import genesis as gs

gs.init()
scene = gs.Scene(show_viewer=True)
scene.build()

# 访问 visualizer
visualizer = scene.visualizer

# 更新可视化
visualizer.update()
```

## 常用操作

### 添加相机

```python
# 添加用于渲染的相机
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
)
```

### 更新视图

```python
# 每步更新可视化
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

### 控制 Viewer

```python
# 访问交互式 viewer
viewer = scene.visualizer.viewer

# 检查 viewer 是否处于活动状态
if scene.visualizer.viewer is not None:
    # 可进行 viewer 操作
    pass
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.Visualizer
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`viewer` - 用于实时可视化的交互式 viewer
- {doc}`renderers/index` - 渲染器后端
- {doc}`cameras/index` - 相机传感器
