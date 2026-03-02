# Solvers

Solvers are the core physics computation engines in Genesis. Each solver implements a specific physics simulation method optimized for different types of materials and phenomena.

## Available Solvers

| Solver | Method | Use Cases |
|--------|--------|-----------|
| **RigidSolver** | Rigid body dynamics | Robots, articulated bodies, rigid objects |
| **MPMSolver** | Material Point Method | Deformables, granular, viscous materials |
| **FEMSolver** | Finite Element Method | Elastic/plastic deformable solids |
| **PBDSolver** | Position Based Dynamics | Cloth, soft bodies, particles |
| **SPHSolver** | Smoothed Particle Hydrodynamics | Fluids, liquids |
| **SFSolver** | String/Fiber dynamics | Ropes, cables, hair |
| **ToolSolver** | Kinematic constraints | Tools, end-effectors |

## Solver Base Class

All solvers inherit from the `Solver` base class which defines the interface:

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

## Solver Components

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

## Multi-Solver Simulation

Genesis supports combining multiple solvers in a single scene:

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

## GPU Acceleration

All solvers leverage GPU acceleration through Quadrants (formerly Taichi):

- Parallel computation across particles/elements
- Efficient memory management
- Batched simulation for multiple environments

## See Also

- {doc}`/api_reference/engine/couplers/index` - Multi-physics coupling
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/index` - Solver options
