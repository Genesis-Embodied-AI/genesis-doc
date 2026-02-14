# Couplers

Couplers 处理 Genesis 中不同 solvers 之间的多物理场交互。它们支持模拟不同材料类型相互作用的场景（例如机器人抓取软体物体）。

## 可用的 Couplers

| Coupler | 描述 | 使用场景 |
|---------|-------------|----------|
| **LegacyCoupler** | 基于脉冲的耦合 | 简单交互 |
| **SAPCoupler** | 空间加速 | 高效的 broad-phase |
| **IPCCoupler** | Incremental Potential Contact | 鲁棒的接触 |

## 配置

Couplers 通过 coupler 选项配置：

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.CouplerOptions(
        # Coupler 特定的选项
    ),
)
```

## 多物理场示例

### 机器人 + 软体物体

```python
# 刚体机器人
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))

# 软体 MPM 物体
soft = scene.add_entity(
    gs.morphs.Box(pos=(0.5, 0, 0.5), size=(0.1, 0.1, 0.1)),
    material=gs.materials.MPM.Elastic(),
)

scene.build()

# 耦合自动发生
for i in range(1000):
    scene.step()
```

### 工具 + 流体

```python
# 运动学工具
tool = scene.add_entity(
    gs.morphs.Mesh(file="paddle.obj"),
    material=gs.materials.Tool(),
)

# SPH 流体
fluid = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5)),
    material=gs.materials.SPH.Liquid(),
)
```

## Coupler 类型

```{toctree}
:titlesonly:

legacy_coupler
sap_coupler
ipc_coupler
```

## 另请参阅

- {doc}`/api_reference/engine/solvers/index` - 物理 solvers
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/coupler_options` - Coupler 选项
