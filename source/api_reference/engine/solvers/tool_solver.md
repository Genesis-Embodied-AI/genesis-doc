# ToolSolver

The `ToolSolver` handles kinematic tools and end-effectors that interact with other physics objects.

## Overview

The Tool solver provides:

- Kinematic motion control
- Collision with other solvers (MPM, FEM, etc.)
- Tool-object interaction

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    tool_options=gs.options.ToolOptions(),
)

# Add kinematic tool
tool = scene.add_entity(
    gs.morphs.Mesh(file="tool.obj"),
    material=gs.materials.Tool(),
)

scene.build()

# Kinematically control tool
for i in range(1000):
    tool.set_pos(new_position)
    tool.set_quat(new_orientation)
    scene.step()
```

## Configuration

Key options in `ToolOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `collision_margin` | float | Collision detection margin |

## Interaction with Other Solvers

Tools can interact with:

- MPM particles
- FEM elements
- PBD particles/cloth
- SPH fluids

The coupling is handled automatically by the coupler system.

## See Also

- {doc}`/api_reference/engine/couplers/index` - Coupling with other solvers
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/tool_options` - Full options
