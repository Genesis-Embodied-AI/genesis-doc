# Solvers (求解器)

Solvers 是 Genesis 中的核心物理计算引擎。每个 solver 都实现了一种特定的物理仿真方法，针对不同类型的材料和现象进行了优化。

## 可用的 Solvers

| Solver | Method (方法) | Use Cases (应用场景) |
|--------|---------------|---------------------|
| **RigidSolver** | Rigid body dynamics (刚体动力学) | Robots (机器人), articulated bodies (铰接体), rigid objects (刚体对象) |
| **MPMSolver** | Material Point Method (物质点法) | Deformables (可变形体), granular (颗粒材料), viscous materials (粘性材料) |
| **FEMSolver** | Finite Element Method (有限元法) | Elastic/plastic deformable solids (弹性/塑性可变形固体) |
| **PBDSolver** | Position Based Dynamics (基于位置的动力学) | Cloth (布料), soft bodies (软体), particles (粒子) |
| **SPHSolver** | Smoothed Particle Hydrodynamics (光滑粒子流体动力学) | Fluids (流体), liquids (液体) |
| **SFSolver** | String/Fiber dynamics (绳/纤维动力学) | Ropes (绳索), cables (缆线), hair (头发) |
| **ToolSolver** | Kinematic constraints (运动学约束) | Tools (工具), end-effectors (末端执行器) |

## Solver 基类

所有 solvers 都继承自 `Solver` 基类，该基类定义了接口：

```python
class Solver:
    def build(self):
        """Initialize solver resources."""
        pass

    def reset(self, envs_idx=None):
        """Reset solver state."""
        pass

    def step(self):
        """Advance physics by one substep."""
        pass
```

## Solver 组件

```{toctree}
:titlesonly:

rigid_solver
mpm_solver
fem_solver
pbd_solver
sph_solver
sf_solver
tool_solver
```

## 多 Solver 仿真

Genesis 支持在单个场景中组合多个 solvers：

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# Rigid robot
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# Soft object (MPM)
soft = scene.add_entity(
    gs.morphs.Box(pos=(0.5, 0, 0.5)),
    material=gs.materials.MPM.Elastic(),
)

# Cloth (PBD)
cloth = scene.add_entity(
    gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(),
)

scene.build()

# All solvers step together
for i in range(1000):
    scene.step()
```

## GPU 加速

所有求解器均通过 Quadrants（原 Taichi）实现 GPU 加速：

- Parallel computation across particles/elements (跨粒子/元素的并行计算)
- Efficient memory management (高效的内存管理)
- Batched simulation for multiple environments (多环境的批处理仿真)

## 另请参阅

- {doc}`/api_reference/engine/couplers/index` - 多物理场耦合 (Multi-physics coupling)
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/index` - Solver 选项
