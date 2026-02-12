# File Writers

Genesis 提供文件写入器，用于将仿真数据导出到各种格式。

## 可用的 Writers

| Writer | Format | Description |
|--------|--------|-------------|
| `CSVFileWriter` | `.csv` | 表格数据导出 |
| `NPZFileWriter` | `.npz` | NumPy 压缩数组 |
| `VideoFileWriter` | `.mp4` | 来自相机/视窗的视频 |

## CSVFile

将数据导出为逗号分隔值：

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Record joint positions to CSV
scene.start_recording(
    data_func=lambda: {
        "q0": robot.get_qpos()[0],
        "q1": robot.get_qpos()[1],
        "q2": robot.get_qpos()[2],
    },
    rec_options=gs.recorders.CSVFile(
        filepath="joint_data.csv",
        hz=100,
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

## NPZFile

将数据导出为 NumPy 压缩归档：

```python
scene.start_recording(
    data_func=lambda: {
        "pos": robot.get_pos(),
        "qpos": robot.get_qpos(),
        "qvel": robot.get_qvel(),
    },
    rec_options=gs.recorders.NPZFile(
        filepath="trajectory.npz",
        hz=50,
    ),
)

# ... simulation ...
scene.stop_recording()

# Load recorded data
import numpy as np
data = np.load("trajectory.npz")
positions = data["pos"]
```

## VideoFile

从相机或视窗录制视频：

```python
cam = scene.add_camera(
    res=(1280, 720),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
)

scene.start_recording(
    data_func=lambda: cam.render(rgb=True),
    rec_options=gs.recorders.VideoFile(
        filepath="simulation.mp4",
    ),
)

for i in range(300):
    scene.step()
scene.stop_recording()
```

## 配置选项

### 通用选项

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `filepath` | str | Required | 输出文件路径 |
| `hz` | float | None | 录制频率 |
| `async_mode` | bool | False | 后台处理 |

### VideoFileWriter 选项

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fps` | int | 30 | 视频帧率 |
| `codec` | str | "libx264" | 视频编解码器 |

## API 参考

```{eval-rst}
.. automodule:: genesis.recorders.file_writers
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`index` - 录制概述
- {doc}`plotters` - 实时可视化
