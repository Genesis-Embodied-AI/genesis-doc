# Recorder

`Recorder` 类是 Genesis 中所有录制功能的基类。它提供了捕获和处理仿真数据的接口。

## 概述

Recorders:

- 以指定频率捕获数据
- 支持同步或异步处理数据
- 支持构建/清理生命周期
- 可在 episode 之间重置

## 创建自定义 Recorders

```python
import genesis as gs
from genesis.recorders import Recorder

class MyRecorder(Recorder):
    def __init__(self, manager, options, data_func):
        super().__init__(manager, options, data_func)
        self.data_buffer = []

    def build(self):
        super().build()
        self.data_buffer = []

    def process(self, data, cur_time):
        self.data_buffer.append({
            "time": cur_time,
            "data": data,
        })

    def cleanup(self):
        # Save or finalize data
        print(f"Recorded {len(self.data_buffer)} samples")
        self.data_buffer = []

    def reset(self, envs_idx=None):
        self.data_buffer = []
```

## 生命周期

1. **`__init__`**: 配置 recorder 选项
2. **`build()`**: 初始化资源（在 scene 构建时调用）
3. **`process(data, time)`**: 处理每个数据样本（在录制期间调用）
4. **`cleanup()`**: 完成并释放资源（在录制停止时调用）
5. **`reset()`**: 为新 episode 重置状态

## API 参考

```{eval-rst}
.. autoclass:: genesis.recorders.base_recorder.Recorder
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`recorder_manager` - 管理多个 recorders
- {doc}`file_writers` - 内置文件写入器
- {doc}`plotters` - 内置绘图器
