# ToolSolver

The `ToolSolver` handles kinematic tools and end-effectors that drive other physics objects through one-way coupling.

## Overview

The tool solver provides:

- Kinematic motion control of a tool entity.
- One-way coupling into the soft solvers (MPM, FEM, PBD, SPH).
- Tool-object interaction without internal tool dynamics.

A ToolEntity has no internal dynamics and is built from a single mesh. It is a temporary workaround for differentiable rigid-soft interaction and will be removed once the RigidSolver supports differentiability directly.

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    tool_options=gs.options.ToolOptions(),
)

# Add a kinematic tool
tool = scene.add_entity(
    gs.morphs.Mesh(file="tool.obj"),
    material=gs.materials.Tool(),
)

scene.build()

# Drive the tool kinematically
for i in range(1000):
    tool.set_position(new_position)      # (x, y, z), meters
    tool.set_quaternion(new_orientation)  # (w, x, y, z), scalar-first
    scene.step()
```

## Configuration

Key options in `ToolOptions`:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dt` | float | inherited | Substep duration in seconds. Inherits from `SimOptions` if not set. |
| `floor_height` | float | inherited | Floor height in meters. Inherits from `SimOptions` if not set. |

## Material parameters

`gs.materials.Tool` parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `friction` | `0.0` | Friction coefficient. |
| `coup_softness` | `0.01` | Softness of the coupling interaction. |
| `collision` | `True` | Whether the tool participates in collision. |
| `sdf_res` | `128` | Resolution of the signed-distance-field grid. |

## Interaction with other solvers

Tools couple one way into the soft solvers:

- MPM particles
- FEM elements
- PBD particles and cloth
- SPH fluids

The coupling is handled automatically by the coupler.

## See also

- {doc}`/api_reference/engine/couplers/index` — coupling with other solvers.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/tool_options` — full options.
