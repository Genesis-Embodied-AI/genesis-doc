# LegacyCoupler

`LegacyCoupler` 为不同的物理 solvers 之间提供基本的基于冲量的耦合。

## 概述

Legacy coupler：

- Uses impulse-based contact resolution (使用基于冲量的接触解析)
- Handles rigid-soft interactions (处理刚体-软体交互)
- Simple and fast for basic scenarios (对基本场景简单且快速)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.LegacyCouplerOptions(
        friction=0.5,
    ),
)
```

## 另请参阅

- {doc}`index` - Coupler 概述
- {doc}`sap_coupler` - 空间加速
