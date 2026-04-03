# Couplers

Couplers handle multi-physics interactions between different solvers in Genesis. They enable simulating scenarios where different material types interact (e.g., a robot grasping a soft object).

## Available Couplers

| Coupler | Description | Use Case |
|---------|-------------|----------|
| **LegacyCoupler** | Impulse-based coupling | Simple interactions |
| **SAPCoupler** | Spatial acceleration | Efficient broad-phase |
| **IPCCoupler** | Incremental Potential Contact | Robust contact |

## Configuration

Couplers are configured through coupler options:

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    coupler_options=gs.options.CouplerOptions(
        # Coupler-specific options
    ),
)
```

## Multi-Physics Examples

### Robot + Soft Object

```python
# Rigid robot
robot = scene.add_entity(gs.morphs.URDF(file="gripper.urdf"))

# Soft MPM object
soft = scene.add_entity(
    gs.morphs.Box(pos=(0.5, 0, 0.5), size=(0.1, 0.1, 0.1)),
    material=gs.materials.MPM.Elastic(),
)

scene.build()

# Coupling happens automatically
for i in range(1000):
    scene.step()
```

### Tool + Fluid

```python
# Kinematic tool
tool = scene.add_entity(
    gs.morphs.Mesh(file="paddle.obj"),
    material=gs.materials.Tool(),
)

# SPH fluid
fluid = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5)),
    material=gs.materials.SPH.Liquid(),
)
```

## Coupler Types

```{toctree}
:titlesonly:

legacy_coupler
sap_coupler
ipc_coupler
```

## See Also

- {doc}`/api_reference/engine/solvers/index` - Physics solvers
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/coupler_options` - Coupler options
