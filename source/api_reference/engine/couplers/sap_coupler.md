# SAPCoupler

`SAPCoupler` (Sweep and Prune，扫描和剪枝) 为多物理场耦合提供高效的空间加速。

## 概述

SAP coupler：

- Uses sweep-and-prune for broad-phase collision (使用扫描和剪枝进行粗粒度碰撞检测)
- Efficient for large numbers of objects (对大量对象高效)
- Reduces narrow-phase checks (减少细粒度检测)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

## 另请参阅

- {doc}`index` - Coupler 概述
- {doc}`ipc_coupler` - IPC 耦合
