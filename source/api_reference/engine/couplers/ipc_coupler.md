# IPCCoupler

`IPCCoupler` (Incremental Potential Contact，增量势能接触) 为多物理场场景提供稳健的接触处理。

## 概述

IPC 耦合：

- Variational contact formulation (变分接触公式)
- Guaranteed intersection-free trajectories (保证无交叉轨迹)
- Robust for challenging contact scenarios (对复杂接触场景具有稳健性)
- Higher computational cost (较高的计算成本)

## 使用方法

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        d_hat=0.001,  # Contact distance threshold (接触距离阈值)
    ),
)
```

## 何时使用 IPC

- Complex deformable-deformable contact (复杂的可变形体-可变形体接触)
- Scenarios requiring intersection-free guarantees (需要无交叉保证的场景)
- When stability is more important than speed (当稳定性比速度更重要时)

## 另请参阅

- {doc}`index` - Coupler 概述
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/coupler_options` - Coupler 选项
