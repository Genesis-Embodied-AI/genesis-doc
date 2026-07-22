# `ToolSolver`

The `ToolSolver` handles kinematic tools and end-effectors that drive other physics objects through one-way coupling into the soft solvers (MPM, FEM, PBD, SPH). A `ToolEntity` has no internal dynamics and is built from a single mesh. It is a temporary workaround for differentiable rigid-soft interaction and will be removed once the `RigidSolver` supports differentiability directly.

## Usage

The solver activates when the scene contains a tool entity, added with the `gs.materials.Tool` material. Configure it through `ToolOptions`; see {doc}`/api_reference/engine/solvers/tool_options` for the full option set.

```python
tool = scene.add_entity(
    gs.morphs.Mesh(file="tool.obj"),
    material=gs.materials.Tool(),
)
```

The tool is then driven kinematically each step with `tool.set_position(...)` and `tool.set_quaternion(...)`.

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
