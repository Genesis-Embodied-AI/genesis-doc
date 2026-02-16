# 物理引擎

Genesis 将多个物理 solver 集成到统一的框架中，支持多种物理现象的仿真，包括刚体、软体、流体及其相互作用。

## 架构概览

```
Scene
└── Simulator
    ├── Solvers (物理计算)
    │   ├── RigidSolver - 刚体动力学
    │   ├── MPMSolver - Material Point Method
    │   ├── FEMSolver - Finite Element Method
    │   ├── PBDSolver - Position Based Dynamics
    │   ├── SPHSolver - Smoothed Particle Hydrodynamics
    │   ├── SFSolver - String/Fiber 动力学
    │   └── ToolSolver - 运动学约束
    │
    └── Couplers (物理交互)
        ├── LegacyCoupler - 基于脉冲的耦合
        ├── SAPCoupler - 空间加速
        └── IPCCoupler - Incremental Potential Contact
```

## 仿真循环

典型的仿真步包括：

1. **Pre-step**: 准备 solver 状态
2. **Solver steps**: 每个 solver 推进其物理计算
3. **Coupling**: 处理不同物理类型之间的交互
4. **Post-step**: 更新渲染状态、传感器

```python
import genesis as gs

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,          # 时间步长
        substeps=4,       # 每步的物理子步数
        gravity=(0, 0, -9.81),
    ),
)

# 添加 entities...
scene.build()

# 每个 step() 执行完整的仿真循环
for i in range(1000):
    scene.step()
```

## Solver 选择

Solvers 根据 entity 类型和 materials 自动选择：

| Entity/Material | Solver |
|-----------------|--------|
| `RigidEntity`, URDF, MJCF | RigidSolver |
| `MPMEntity`, MPM materials | MPMSolver |
| `FEMEntity`, FEM materials | FEMSolver |
| `PBDEntity`, cloth/soft materials | PBDSolver |
| `SPHEntity`, SPH liquid | SPHSolver |
| String/fiber materials | SFSolver |

## Solver 配置

每个 solver 有专用的配置选项：

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,
        substeps=4,
    ),
    rigid_options=gs.options.RigidOptions(
        enable_collision=True,
        enable_joint_limit=True,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(-1, -1, 0),
        upper_bound=(1, 1, 2),
    ),
)
```

## 组件

```{toctree}
:titlesonly:

solvers/index
couplers/index
states/index
```

## 另请参阅

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/index` - Solver 配置
- {doc}`/api_reference/entity/index` - 每种 solver 对应的 Entity 类型
