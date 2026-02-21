# 🎑 查看器交互

Genesis viewer支持鼠标和键盘交互，用于相机控制、录制、可视化切换等功能。
此功能可以通过自定义按键绑定和查看器插件轻松扩展。


## 添加按键绑定

在 `scene.build()` 之前使用 `scene.viewer.register_keybinds(...)` 注册按键绑定。


```python
import genesis.vis.keybindings as kb

...

is_running = True

def stop():
    global is_running
    is_running = False

scene.viewer.register_keybinds(
    kb.Keybind("greetings", kb.Key.G, kb.KeyAction.PRESS, callback=lambda: print("Hello!")),
    kb.Keybind("quit", kb.Key.ESCAPE, kb.KeyAction.PRESS, callback=stop),
    # 添加任意数量的按键绑定！
)
scene.build()

while is_running:
    scene.step()
```

```{figure} ../../_static/images/keybindings_instructions.png
:alt: 查看器覆盖层显示键盘说明，包括插件按键绑定
```
注册的按键绑定会显示在查看器的说明覆盖层中，以便用户一目了然地发现控制方式。


要在创建场景时禁用默认查看器控件和/或隐藏帮助文本，请设置相应的选项以便于使用：

```python
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        enable_help_text=False,         # 隐藏说明文本
        enable_default_keybinds=False,  # 禁用默认查看器快捷键
    ),
)
```


## 查看器插件

查看器插件通过自定义输入处理和可视化来扩展交互式场景查看器。
它们接收鼠标和键盘事件，可以在每帧绘制调试几何体，并在每个模拟步骤运行逻辑——非常适合用于在网格上拾取点或用鼠标拖动刚体等工具。

在 `scene.build()` 之前使用 `scene.viewer.add_plugin(plugin)` 添加插件。
示例脚本可在 `examples/viewer_plugin/` 下找到。


### 鼠标交互插件

**`MouseInteractionPlugin`** 允许您点击并拖动场景中的刚体。
您可以通过直接设置刚体位置（默认）来移动刚体，或施加弹簧力以获得更真实的物理效果。

完整示例脚本可在 `examples/viewer_plugin/mouse_interaction.py` 找到。
使用 `--use_force` 标志启用弹簧力代替位置控制。

```python
scene.viewer.add_plugin(
    gs.vis.viewer_plugins.MouseInteractionPlugin(
        use_force=True,  # False = 设置位置, True = 弹簧力
        spring_const=1000.0,
        color=(0.1, 0.6, 0.8, 0.6),
    )
)
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/viewer_plugin_mouse_spring.mp4" type="video/mp4">
</video>


### 自定义插件

您可以通过继承 `ViewerPlugin`（如果需要屏幕到世界的光线投射，则继承 `RaycasterViewerPlugin`）来实现自定义插件，并使用 `scene.viewer.add_plugin()` 添加它们。

#### ViewerPlugin 基类

自定义插件继承 `gs.vis.viewer_plugins.ViewerPlugin`。
场景构建后，查看器会调用 `build(viewer, camera, scene)`；请重写此方法以存储引用并设置状态。

事件钩子返回 `EVENT_HANDLED`（或 `True`）表示事件已被消耗，或返回 `None` 以让其他插件或默认查看器处理。

| 方法 | 描述 |
|--------|-------------|
| `on_mouse_motion(x, y, dx, dy)` | 鼠标移动 |
| `on_mouse_drag(x, y, dx, dy, buttons, modifiers)` | 按住按钮拖动鼠标 |
| `on_mouse_press(x, y, buttons, modifiers)` | 鼠标按钮按下（在初始按下时调用一次） |
| `on_mouse_release(x, y, buttons, modifiers)` | 鼠标按钮释放 |
| `on_mouse_scroll(x, y, dx, dy)` | 鼠标滚轮 |
| `on_key_press(key, modifiers)` | 键盘按键按下 |
| `on_key_release(key, modifiers)` | 键盘按键释放 |
| `on_resize(width, height)` | 窗口大小改变 |
| `update_on_sim_step()` | 每次 `scene.step()` 时调用 |
| `on_draw()` | 每帧调用，用于自定义绘制 |
| `on_close()` | 查看器关闭时调用 |

```python
from genesis.vis.viewer_plugins import ViewerPlugin, EVENT_HANDLED, EVENT_HANDLE_STATE

class MyPlugin(ViewerPlugin):
    def build(self, viewer, camera, scene):
        super().build(viewer, camera, scene)
        # self.viewer, self.camera, self.scene 已设置

    def on_key_press(self, symbol: int, modifiers: int) -> EVENT_HANDLE_STATE:
        if symbol == ord("x"):
            # 执行某些操作
            return EVENT_HANDLED
        return None

    def on_draw(self) -> None:
        # 例如通过 self.scene.draw_debug_*() 绘制调试几何体
        pass
```

#### RaycasterViewerPlugin 和屏幕空间光线

对于点击选择或 3D 拖动行为，您需要从相机穿过鼠标位置的光线。
继承 `RaycasterViewerPlugin` 而不是 `ViewerPlugin`；它维护一个光线投射器并提供 `_screen_position_to_ray(x, y)`，返回世界坐标系中的 `Ray`（原点和方向）。

`RaycasterViewerPlugin` 还会重写 `update_on_sim_step()`，以便光线投射器在每个步骤与场景保持同步。

```python
from genesis.vis.viewer_plugins import RaycasterViewerPlugin, EVENT_HANDLED

class PickerPlugin(RaycasterViewerPlugin):
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button != 1:
            return None
        ray = self._screen_position_to_ray(x, y)
        hit = self._raycaster.cast(*ray)
        if hit is not None and hit.geom:
            link = hit.geom.link
            world_pos = hit.position
            # ...
            return EVENT_HANDLED
        return None
```

使用 `scene.viewer.register_keybinds()` 注册按键（例如退出、切换模式）；这些按键绑定会显示在查看器的键盘说明覆盖层中，以便用户轻松发现它们。


#### 示例：网格点选择器

**`MeshPointSelectorPlugin`** 使用鼠标光线投射来选择刚体网格上的点。
点击可添加或删除点；选中的点显示为球体，可以吸附到网格。
关闭时，插件将选中的点（以链接局部坐标表示）写入 CSV 文件，这在需要获取局部位置以在实体上放置传感器时非常有用。

完整示例脚本可在 `examples/viewer_plugin/mesh_point_selector.py` 找到。

```python
from genesis.vis.viewer_plugins import MeshPointSelectorPlugin

scene.viewer.add_plugin(
    MeshPointSelectorPlugin(
        sphere_radius=0.004,
        sphere_color=(0.1, 0.3, 1.0, 1.0),
        hover_color=(0.3, 0.5, 1.0, 1.0),
        grid_snap=(-1.0, 0.01, 0.01),  # -1 = 该轴不吸附
        output_file="selected_points.csv",
    )
)
scene.build()
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/viewer_plugin_mesh_point.mp4" type="video/mp4">
</video>
