# RecorderManager

`RecorderManager` 协调多个 recorders，管理它们的生命周期和数据分发。

## 概述

RecorderManager:

- 管理 recorders 集合
- 将数据分派到适当的 recorders
- 处理录制会话的启动/停止
- 协调构建和清理阶段

## 用法

RecorderManager 通常通过 Scene 访问：

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# Add multiple recorders
scene.add_recorder(
    gs.recorders.NPZFileWriter(filepath="data.npz"),
    data_func=lambda: robot.get_qpos(),
)

scene.add_recorder(
    gs.recorders.MPLLinePlotter(title="Positions"),
    data_func=lambda: robot.get_qpos(),
)

# Start all recorders
scene.start_recording()

for i in range(1000):
    scene.step()

# Stop all recorders
scene.stop_recording()
```

## 录制控制

```python
# Start recording all registered recorders
scene.start_recording()

# Check recording status
if scene.is_recording:
    print("Currently recording")

# Stop recording and trigger cleanup
scene.stop_recording()

# Stop recording and save video (if viewer is active)
scene.stop_recording(save_to="output.mp4")
```

## API 参考

```{eval-rst}
.. autoclass:: genesis.recorders.recorder_manager.RecorderManager
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`recorder` - 基 recorder 类
- {doc}`/api_reference/scene/scene` - Scene 录制方法
