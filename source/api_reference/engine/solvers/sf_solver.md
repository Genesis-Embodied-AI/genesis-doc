# SFSolver

The `SFSolver` (String/Fiber) handles simulation of 1D structures like ropes, cables, and hair.

## Overview

The SF solver simulates:

- Inextensible constraints
- Bending resistance
- Twist resistance
- Contact with other objects

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sf_options=gs.options.SFOptions(
        iterations=20,
    ),
)

# Add rope/cable
rope = scene.add_entity(
    gs.morphs.Mesh(file="rope.obj"),
    material=gs.materials.SF.Rope(
        stretch_stiffness=1.0,
        bend_stiffness=0.1,
    ),
)

scene.build()

for i in range(1000):
    scene.step()
```

## Configuration

Key options in `SFOptions`:

| Option | Type | Description |
|--------|------|-------------|
| `iterations` | int | Constraint iterations |
| `damping` | float | Velocity damping |

## See Also

- {doc}`/api_reference/options/simulator_coupler_and_solver_options/sf_options` - Full options
