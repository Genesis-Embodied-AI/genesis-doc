# `ToolSolver`

The `ToolSolver` handles kinematic tools and end-effectors that drive other physics objects through one-way coupling into the soft solvers (MPM, FEM, PBD, SPH). A `ToolEntity` has no internal dynamics and is built from a single mesh. It is a temporary workaround for differentiable rigid-soft interaction and will be removed once the `RigidSolver` supports differentiability directly.

## Usage

The solver activates when the scene contains a tool entity. Configure it through `ToolOptions`; see {doc}`/api_reference/engine/solvers/tool_options` for the full option set.

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

## Interaction with other solvers

Tools couple one way into the soft solvers:

- MPM particles
- FEM elements
- PBD particles and cloth
- SPH fluids

The coupling is handled automatically by the coupler.

## See also

- {doc}`/api_reference/entity/material/tool`: the tool material and its parameters.
- {doc}`/api_reference/engine/couplers/index`: coupling with other solvers.
- {doc}`/api_reference/engine/solvers/tool_options`: full options.
