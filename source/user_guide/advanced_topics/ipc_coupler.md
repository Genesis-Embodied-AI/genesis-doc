# ⚡ IPC Coupler

Genesis provides Incremental Potential Contact (IPC) coupling for high-fidelity deformable-rigid interactions.

## Requirements

Requires `libuipc` library (build from https://github.com/spiriMirror/libuipc).

## Basic Setup

```python
import genesis as gs

dt = 0.01
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=dt, gravity=(0.0, 0.0, -9.8)),
    coupler_options=gs.options.IPCCouplerOptions(
        dt=dt,
        gravity=(0.0, 0.0, -9.8),
    ),
)
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dt` | 0.001 | Time step for IPC simulation |
| `contact_d_hat` | 0.001 | Contact barrier distance |
| `contact_friction_mu` | 0.5 | Friction coefficient |
| `ipc_constraint_strength` | (100, 100) | (translation, rotation) coupling strength |
| `two_way_coupling` | True | Forces from IPC affect rigid bodies |
| `IPC_self_contact` | False | Enable rigid-rigid self-collision |
| `enable_ipc_gui` | False | Polyscope visualization |

## Cloth Simulation

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=2e-3,
        contact_d_hat=0.01,
        contact_friction_mu=0.3,
        enable_ipc_gui=True,
    ),
)

cloth = scene.add_entity(
    morph=gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.FEM.Cloth(
        E=10e5,
        nu=0.499,
        rho=200,
        thickness=0.001,
        bending_stiffness=50.0,
    ),
)
```

## Robot Grasping

```python
scene = gs.Scene(
    coupler_options=gs.options.IPCCouplerOptions(
        dt=1e-2,
        ipc_constraint_strength=(100, 100),
        contact_friction_mu=0.8,
        two_way_coupling=True,
    ),
)

franka = scene.add_entity(gs.morphs.MJCF(file="panda.xml"))

# Filter which links participate in IPC
scene.sim.coupler.set_ipc_link_filter(
    entity=franka,
    link_names=["left_finger", "right_finger"],
)

cube = scene.add_entity(
    morph=gs.morphs.Box(),
    material=gs.materials.FEM.Elastic(E=5e3, nu=0.45, rho=1000),
)
```

## When to Use IPC

**Use IPC for:**
- Cloth/fabric simulation with collision
- FEM objects interacting with rigid bodies
- High-quality grasping simulation
- Stable constraint-based contact resolution

**Use LegacyCoupler for:**
- Simple rigid-MPM, rigid-SPH interactions
- Lower computational overhead
- When IPC library unavailable

## Contact Handling

| Interaction | IPC Behavior |
|-------------|--------------|
| FEM-FEM | Always enabled |
| FEM-Rigid | Always enabled |
| Rigid-Rigid | `IPC_self_contact` option |
| Cloth-Cloth | Always enabled (self-collision) |

## Performance Tips

- Match `contact_d_hat` to mesh resolution (0.5-2mm typical)
- Higher `ipc_constraint_strength` = stiffer but potentially unstable
- Use `disable_genesis_ground_contact=True` to avoid double-counting ground collision
