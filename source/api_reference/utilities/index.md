# 工具与辅助函数

Genesis 提供各种 utility 函数、常量和辅助类用于常见操作。

## 概览

本节涵盖：

- **Constants**: Joint 类型、几何类型、后端的枚举
- **Device utilities**: 平台检测、设备选择
- **Tensor utilities**: 数组/tensor 转换
- **Geometry utilities**: 变换操作
- **File I/O**: 路径工具、URDF/MJCF 解析

## 快速参考

### 初始化

```python
import genesis as gs

# 使用默认设置初始化
gs.init()

# 使用特定后端初始化
gs.init(backend=gs.cpu)      # CPU 后端
gs.init(backend=gs.gpu)      # GPU 后端（CUDA/Metal）

# 使用自定义设置
gs.init(
    seed=42,              # 随机种子
    precision="32",       # 浮点精度
    debug=False,          # 调试模式
    backend=gs.gpu,
)
```

### 全局变量

`gs.init()` 后，以下全局变量可用：

| 变量 | 描述 |
|----------|-------------|
| `gs.platform` | 平台字符串（"Linux"、"macOS" 等） |
| `gs.device` | PyTorch 设备 |
| `gs.backend` | 活动后端枚举 |
| `gs.EPS` | 数值 epsilon |

## 组件

```{toctree}
:titlesonly:

constants
device
tensor_utils
geometry
file_io
```

## 另请参阅

- {doc}`/api_reference/options/index` - 配置选项
