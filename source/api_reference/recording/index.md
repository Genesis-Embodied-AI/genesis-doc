# 记录与回放

Genesis 提供灵活的记录系统用于捕获仿真数据。这支持数据日志记录、可视化、视频生成和仿真结果分析。

## 概览

记录系统包括：

- **Recorder**: 处理仿真数据的基类
- **RecorderManager**: 协调多个 recorders
- **FileWriters**: 将数据导出到文件（CSV、NPZ、Video）
- **Plotters**: 数据的实时可视化

## 快速开始

### 录制视频

```python
import genesis as gs

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 1)))
scene.build()

# 开始录制
scene.start_recording()

for i in range(200):
    scene.step()
    scene.visualizer.update()

# 停止并保存
scene.stop_recording(save_to="simulation.mp4")
```

### 录制自定义数据

```python
# 定义要记录的数据
def get_robot_state():
    return {
        "position": robot.get_pos(),
        "velocity": robot.get_vel(),
        "joint_positions": robot.get_qpos(),
    }

# 使用 recorder 选项开始录制
scene.start_recording(
    data_func=get_robot_state,
    rec_options=gs.recorders.NPZFile(
        filepath="robot_data.npz",
        hz=100,  # 录制频率
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

### 实时绘图

```python
# 实时绘制 joint 位置
scene.start_recording(
    data_func=lambda: robot.get_qpos(),
    rec_options=gs.recorders.MPLLinePlot(
        title="Joint Positions",
    ),
)

for i in range(1000):
    scene.step()
scene.stop_recording()
```

## 组件

```{toctree}
:titlesonly:

recorder
recorder_manager
file_writers
plotters
```

## 录制工作流程

1. **定义数据函数**: 返回要记录的数据的可调用对象
2. **创建 recorder**: 实例化 recorder（FileWriter、Plotter 等）
3. **添加到 scene**: 向 scene 注册 recorder
4. **开始录制**: 开始数据捕获
5. **运行仿真**: 执行仿真步
6. **停止录制**: 完成并保存数据

## 配置

所有 recorders 共享通用选项：

| 选项 | 类型 | 描述 |
|--------|------|-------------|
| `hz` | float | 录制频率（采样/秒） |
| `async_mode` | bool | 在后台线程中处理数据 |

## 另请参阅

- {doc}`/api_reference/visualization/index` - 视觉输出
- {doc}`/api_reference/scene/index` - Scene 管理
