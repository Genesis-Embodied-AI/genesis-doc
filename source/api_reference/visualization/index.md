# 可视化与渲染

Genesis 提供全面的可视化系统用于渲染仿真。系统支持多种渲染后端，包括用于实时查看的快速光栅化和用于照片级真实感输出的光线追踪。

## 概览

可视化系统围绕三个主要组件构建：

- **Visualizer**: 管理 cameras、viewers 和 renderers 的主协调器
- **Viewer**: 用于实时可视化的交互式窗口，带有 camera 控制
- **Renderers**: 后端特定的渲染引擎（Rasterizer、Raytracer、BatchRenderer）

## 快速开始

```python
import genesis as gs

gs.init()

# 创建带有可视化的 scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3, 0, 2),
        camera_lookat=(0, 0, 0.5),
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
    ),
)

# 添加 entities 并 build
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

# 交互式查看
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

## 组件

```{toctree}
:titlesonly:

visualizer
viewer
renderers/index
cameras/index
lights
```

## 另请参阅

- {doc}`/api_reference/options/renderer/index` - Renderer 配置选项
- {doc}`/api_reference/options/options` - Viewer 和可视化选项
