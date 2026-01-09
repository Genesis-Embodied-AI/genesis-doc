# Recorder

The `Recorder` class is the base class for all recording functionality in Genesis. It provides the interface for capturing and processing simulation data.

## Overview

Recorders:

- Capture data at specified frequencies
- Process data synchronously or asynchronously
- Support building/cleanup lifecycle
- Can be reset between episodes

## Creating Custom Recorders

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

## Lifecycle

1. **`__init__`**: Configure recorder options
2. **`build()`**: Initialize resources (called when scene builds)
3. **`process(data, time)`**: Handle each data sample (called during recording)
4. **`cleanup()`**: Finalize and release resources (called when recording stops)
5. **`reset()`**: Reset state for new episode

## API Reference

```{eval-rst}
.. autoclass:: genesis.recorders.base_recorder.Recorder
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`recorder_manager` - Managing multiple recorders
- {doc}`file_writers` - Built-in file writers
- {doc}`plotters` - Built-in plotters
