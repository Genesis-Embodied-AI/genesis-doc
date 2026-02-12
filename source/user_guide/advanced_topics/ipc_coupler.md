# ⚡ IPC Coupler

Genesis 为高精度可变形体-刚体交互提供增量势能接触 (IPC) 耦合。

## 要求

需要 `libuipc` 库（从 https://github.com/spiriMirror/libuipc 构建）。

## 基本设置

```python
import genesis as gs

dt = 0.01
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=dt, gravity=(0.0, 0.0, -9.8)),
    coupler_options=gs.options.IPCCouplerOptions(
        dt=dt,
        gravity=(0.0, 0.0, -9.8),
    ),
)
```

## 关键参数

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `dt` | 0.001 | IPC 模拟的时间步长 |
| `contact_d_hat` | 0.001 | 接触屏障距离 |
| `contact_friction_mu` | 0.5 | 摩擦系数 |
| `ipc_constraint_strength` | (100, 100) |（平移、旋转）耦合强度 |
| `two_way_coupling` | True | IPC 产生的力影响刚体 |
| `IPC_self_contact` | False | 启用刚体-刚体自碰撞 |
| `enable_ipc_gui` | False | Polyscope 可视化 |

## 布料模拟

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=2e-3,
        contact_d_hat=0.01,
        contact_friction_mu=0.3,
        enable_ipc_gui=True,
    ),
)

cloth = scene.add_entity(
    morph=gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.FEM.Cloth(
        E=10e5,
        nu=0.499,
        rho=200,
        thickness=0.001,
        bending_stiffness=50.0,
    ),
)
```

## 机器人抓取

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=1e-2,
        ipc_constraint_strength=(100, 100),
        contact_friction_mu=0.8,
        two_way_coupling=True,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))

# 过滤哪些连杆参与 IPC
scene.sim.coupler.set_ipc_link_filter(
    entity=franka,
    link_names=["left_finger", "right_finger"],
)

cube = scene.add_entity(
    morph=gs.morphs.Box(),
    material=gs.materials.FEM.Elastic(E=5e3, nu=0.45, rho=1000),
)
```

## 何时使用 IPC

**使用 IPC：**
- 带碰撞的布料/织物模拟
- FEM 对象与刚体交互
- 高质量抓取模拟
- 稳定的基于约束的接触解析

**使用 LegacyCoupler：**
- 简单的刚体-MPM、刚体-SPH 交互
- 较低的计算开销
- 当 IPC 库不可用时

## 接触处理

| 交互 | IPC 行为 |
|-------------|--------------|
| FEM-FEM | 始终启用 |
| FEM-Rigid | 始终启用 |
| Rigid-Rigid | `IPC_self_contact` 选项 |
| Cloth-Cloth | 始终启用（自碰撞） |

## 性能提示

- 将 `contact_d_hat` 匹配到网格分辨率（典型 0.5-2mm）
- 更高的 `ipc_constraint_strength` = 更硬但可能不稳定
- 使用 `disable_genesis_ground_contact=True` 避免重复计算地面碰撞
