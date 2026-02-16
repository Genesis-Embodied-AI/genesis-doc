# Viewer

`Viewer` 类提供了一个交互式窗口，用于实时可视化仿真。用户可以通过鼠标控制来浏览场景、检查对象以及控制仿真播放。

## 概述

Viewer 是一个可选组件，提供以下功能：

- 仿真的实时 3D 渲染
- 基于鼠标的相机导航（轨道、平移、缩放）
- 用于控制仿真的键盘快捷键
- 实体选择和高亮显示
- 渲染状态可视化

## 快速开始

```python
import genesis as gs

gs.init()

# 创建带有交互式 viewer 的场景
scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3, 0, 2),
        camera_lookat=(0, 0, 0.5),
        res=(1280, 720),
        max_FPS=60,
    ),
)

scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

# 在 viewer 中运行
for i in range(1000):
    scene.step()
    scene.visualizer.update()
```

## 相机控制

| 控制方式 | 操作 |
|---------|------|
| 左键 + 拖动 | 轨道旋转相机 |
| 右键 + 拖动 | 平移相机 |
| 滚轮 | 放大/缩小 |
| 中键 + 拖动 | 缩放 |

## 键盘快捷键

| 按键 | 操作 |
|-----|------|
| Space | 暂停/恢复仿真 |
| R | 重置相机到初始位置 |
| Esc | 关闭 viewer |

## 配置

通过 `ViewerOptions` 配置 viewer：

```python
viewer_options = gs.options.ViewerOptions(
    res=(1920, 1080),          # 分辨率
    camera_pos=(5, 0, 3),       # 初始相机位置
    camera_lookat=(0, 0, 0),    # 相机目标点
    camera_fov=45,              # 视野角度
    max_FPS=60,                 # 最大帧率
    run_in_thread=True,         # 在单独线程中运行 viewer
    enable_interaction=True,    # 启用鼠标/键盘交互
)
```

## 无头模式（Headless Mode）

对于没有显示环境的情况（服务器、CI），禁用 viewer：

```python
scene = gs.Scene(show_viewer=False)
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.viewer.Viewer
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`visualizer` - 主可视化控制器
- {doc}`/api_reference/options/options` - ViewerOptions 配置
