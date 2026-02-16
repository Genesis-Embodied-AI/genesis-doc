# Device & Platform Utilities

用于检测和配置计算平台和设备的函数。

## 平台检测

```python
import genesis as gs

# Get platform before init
platform = gs.get_platform()
print(platform)  # "Linux", "macOS", or "Windows"

# After init, access global
gs.init()
print(gs.platform)  # Same result
```

## 设备信息

```python
import genesis as gs

gs.init(backend=gs.gpu)

# Get PyTorch device
device = gs.device
print(device)  # cuda:0, mps:0, cpu, etc.

# Get active backend
backend = gs.backend
print(backend)  # gs.cuda, gs.metal, gs.cpu, etc.
```

## Backend 选择

### 自动选择

```python
# GPU auto-selects based on platform
gs.init(backend=gs.gpu)
# Linux -> CUDA
# macOS -> Metal
```

### 手动选择

```python
# Force specific backend
gs.init(backend=gs.cuda)    # NVIDIA CUDA
gs.init(backend=gs.metal)   # Apple Metal
gs.init(backend=gs.cpu)     # CPU fallback
```

## 随机种子

```python
import genesis as gs

# Set random seed for reproducibility
gs.init(seed=42)

# Or set later
gs.set_random_seed(42)
```

## 全局变量

`gs.init()` 后，以下变量可用：

| Variable | Type | Description |
|----------|------|-------------|
| `gs.platform` | str | 平台: "Linux", "macOS", "Windows" |
| `gs.device` | torch.device | PyTorch 张量设备 |
| `gs.backend` | gs.backend | 活动计算后端 |
| `gs.EPS` | float | 数值 epsilon（例如，1e-15） |

## 类型提示

```python
# Quadrants types
gs.qd_float  # Quadrants float type
gs.qd_int    # Quadrants int type
gs.qd_vec3   # Quadrants 3D vector
gs.qd_mat3   # Quadrants 3x3 matrix

# PyTorch types
gs.tc_float  # PyTorch float dtype
gs.tc_int    # PyTorch int dtype
```

## 另请参阅

- {doc}`constants` - 后端枚举
- {doc}`tensor_utils` - 张量操作
