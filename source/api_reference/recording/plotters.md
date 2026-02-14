# Plotters

Genesis 提供实时绘图 recorders，用于在执行期间可视化仿真数据。

## 可用的 Plotters

| Plotter | Description |
|---------|-------------|
| `MPLLinePlot` | Matplotlib 折线图（时间序列） |
| `MPLImagePlot` | Matplotlib 图像显示 |

## MPLLinePlot

使用 Matplotlib 实时绘制折线图：

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Plot joint positions over time
scene.start_recording(
    data_func=lambda: robot.get_qpos()[:3],  # First 3 joints
    rec_options=gs.recorders.MPLLinePlot(
        title="Joint Positions",
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

### 配置

```python
gs.recorders.MPLLinePlot(
    title="Plot Title",           # 绘图标题
    hz=30,                        # 更新率
)
```

## MPLImagePlot

实时显示图像：

```python
cam = scene.add_camera(res=(320, 240), pos=(3, 0, 2), lookat=(0, 0, 0.5))

scene.start_recording(
    data_func=lambda: cam.render(rgb=True),
    rec_options=gs.recorders.MPLImagePlot(
        title="Camera View",
    ),
)

for i in range(500):
    scene.step()
scene.stop_recording()
```

## Multiple Recorders

您可以通过多次调用 `start_recording` 或直接使用 RecorderManager 来为不同的数据流启动多个 recorders。

## 性能提示

1. **降低更新率**：对复杂绘图使用较低的 `hz`
2. **限制数据点**：使用较小的 `window_size`
3. **使用异步模式**：启用 `async_mode=True` 进行后台更新

## API 参考

```{eval-rst}
.. automodule:: genesis.recorders.plotters
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 录制概述
- {doc}`file_writers` - 文件导出
