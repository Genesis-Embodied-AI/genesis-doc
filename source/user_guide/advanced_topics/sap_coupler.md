# 🔧 SAP Coupler

Genesis 为精确的刚体-FEM 接触处理提供半解析原始 (SAP) 耦合。

## 要求

```python
import genesis as gs

# 必须使用 64 位精度
gs.init(backend=gs.gpu, precision="64")
```

## 基本设置

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True),  # 必需
    coupler_options=gs.options.SAPCouplerOptions(),
)
```

## 关键参数

| 参数 | 默认值 | 描述 |
|-----------|---------|-------------|
| `n_sap_iterations` | 5 | 每步 SAP 求解器迭代次数 |
| `n_pcg_iterations` | 100 | 最大 PCG 求解器迭代次数 |
| `sap_convergence_atol` | 1e-6 | 绝对容差 |
| `sap_convergence_rtol` | 1e-5 | 相对容差 |
| `sap_taud` | 0.1 | 耗散时间尺度 |
| `hydroelastic_stiffness` | 1e8 | 水弹性接触刚度 |
| `point_contact_stiffness` | 1e8 | 点接触刚度 |
| `enable_rigid_fem_contact` | True | 启用刚体-FEM 耦合 |

## 接触类型选项

| 参数 | 可选值 | 描述 |
|-----------|--------|-------------|
| `fem_floor_contact_type` | "tet", "vert", "none" | FEM-地面接触方法 |
| `rigid_floor_contact_type` | "tet", "vert", "none" | 刚体-地面接触 |
| `rigid_rigid_contact_type` | "tet", "none" | 刚体-刚体接触 |

- **"tet"**：默认，基于四面体化（最精确）
- **"vert"**：用于非常粗的网格
- **"none"**：禁用接触类型

## 机器人抓取示例

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=1/60, substeps=2),
    rigid_options=gs.options.RigidOptions(enable_self_collision=False),
    fem_options=gs.options.FEMOptions(use_implicit_solver=True, pcg_threshold=1e-10),
    coupler_options=gs.options.SAPCouplerOptions(
        pcg_threshold=1e-10,
        sap_convergence_atol=1e-10,
        sap_convergence_rtol=1e-10,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(radius=0.02, pos=(0.65, 0.0, 0.02)),
    material=gs.materials.FEM.Elastic(model="linear_corotated", E=1e5, nu=0.4),
)
```

## FEM 仿真

```python
sphere = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.0, 0.0, 0.1), radius=0.1),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4, model="linear_corotated"),
)
```

## 何时使用 SAP

**使用 SAP：**
- 刚体-FEM 交互（机器人抓取可变形体）
- 水弹性接触模型
- 高精度要求
- 可变形物体的操作任务

**使用 LegacyCoupler：**
- 多粒子求解器（MPM、SPH、PBD）
- 可微仿真（SAP 不支持梯度）
- 纯刚体仿真

## 性能

- **更快的收敛**：40 步 vs LegacyCoupler 的 150 步
- **更高的精度**：位置误差 ~1e-3 vs ~5e-3
- **权衡**：需要 64 位精度，FEM 隐式求解器

## 限制

- 仅支持刚体 + FEM 求解器
- 需要 64 位精度 (`precision="64"`)
- FEM 必须使用隐式求解器
- 可微仿真不支持梯度
