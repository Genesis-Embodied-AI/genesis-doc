# IPC coupler

The IPC coupler resolves contact with Incremental Potential Contact, a barrier-based model built on the [libuipc](https://github.com/spiriMirror/libuipc) library. Where the legacy coupler applies impulses and the {doc}`SAP coupler <sap_coupler>` solves a semi-analytic contact problem, IPC advances every coupled body through a single smooth potential whose barrier term grows without bound as surfaces approach. The result is contact that stays intersection-free and stable even under large deformation, which is what makes it the right choice for cloth and heavily deforming soft bodies.

Reach for IPC when accuracy and robustness matter more than speed: cloth with self-collision, FEM solids pressed hard against each other, or a gripper closing on a deformable object. For mixed continuum scenes (MPM, SPH, PBD) or when you only need coarse rigid contact, stay on the default legacy coupler. See {doc}`the couplers overview <index>` for the full comparison.

Under the hood, FEM bodies are coupled directly from their vertex positions, while rigid bodies enter the IPC world as affine bodies (ABD). Time step, gravity, and differentiable-simulation mode come from {doc}`SimOptions </api_reference/engine/simulator>`, so you set them there, not on the coupler.

## Prerequisites

IPC coupling depends on `libuipc`, which is distributed as the `pyuipc` package (imported as `uipc`). It is an optional dependency, not installed with Genesis World by default.

```bash
pip install pyuipc
```

:::{warning}
`pyuipc` currently supports only x86 Linux and Windows, on CPU or an NVIDIA GPU. On any other platform the IPC coupler is unavailable. If the import fails, Genesis World raises an error when you build a scene that uses {py:class}`IPCCouplerOptions <genesis.options.solvers.IPCCouplerOptions>`.
:::

## Minimal example

The complete script is [`examples/IPC_Solver/ipc_objects_falling.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/IPC_Solver/ipc_objects_falling.py): a cloth sheet falls onto a rigid box and a soft FEM ball, all resolved by IPC. Select the coupler by passing `IPCCouplerOptions` to the {doc}`Scene </api_reference/engine/scene>`:

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.02),  # dt and gravity live here, not on the coupler
    coupler_options=gs.options.IPCCouplerOptions(
        contact_d_hat=0.01,  # contact barrier distance (m); size to your mesh resolution
        two_way_coupling=True,  # IPC forces act back on Genesis rigid bodies
    ),
)
```

Entities join the IPC world through their {doc}`material </api_reference/engine/material/index>`. A cloth is an FEM shell:

```python
cloth = scene.add_entity(
    morph=gs.morphs.Mesh(file="path/to/grid20x20.obj", pos=(0.0, 0.0, 1.0)),
    material=gs.materials.FEM.Cloth(
        E=1e5,  # Young's modulus (Pa)
        nu=0.499,  # Poisson's ratio, nearly incompressible
        rho=200,  # density (kg/m3)
        thickness=0.001,  # shell thickness (m)
        bending_stiffness=50.0,
    ),
)
```

A rigid body that should be driven entirely by IPC uses `coup_type="ipc_only"`:

```python
box = scene.add_entity(
    morph=gs.morphs.Box(pos=(-0.25, 0.0, 0.3), size=(0.2, 0.2, 0.2)),
    material=gs.materials.Rigid(rho=500, coup_type="ipc_only"),
)
```

:::{note}
The example downloads a coarse `grid20x20.obj` cloth mesh rather than a dense one. IPC's contact barrier needs the mesh to be coarse relative to `contact_d_hat`; a mesh whose triangles are smaller than the barrier distance triggers thickness violations. Match `contact_d_hat` to your mesh resolution (0.5–2 mm is typical) instead of shrinking it blindly.
:::

## How entities couple

You do not register links with the coupler directly. Instead, each entity's {doc}`Rigid material </api_reference/engine/material/rigid>` declares how it participates through `coup_type`:

- **`two_way_soft_constraint`:** Genesis and IPC exchange forces through a soft position-and-orientation constraint. Use it for a floating-base robot or any rigid body whose motion Genesis controls but that must also feel contact.
- **`external_articulation`:** joint-level coupling for articulated robots: IPC couples at the dof level rather than per link. Use it for a fixed-base arm.
- **`ipc_only`:** IPC owns the body's dynamics (gravity and collision) and copies the resulting transform back to Genesis one-way. Use it for passive rigid props.

When `coup_type` is `None` (the default), Genesis picks one from the entity type: `external_articulation` for fixed-base robots, `two_way_soft_constraint` for floating-base robots, and `ipc_only` for non-articulated objects.

To restrict a `two_way_soft_constraint` robot so that only certain links participate (for example, coupling a gripper's fingers but not its arm), pass `coup_links`:

```python
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda_non_overlap.xml"),
    material=gs.materials.Rigid(
        coup_type="two_way_soft_constraint",
        coup_links=("left_finger", "right_finger"),  # only these links couple
        coup_friction=0.8,
    ),
)
```

## Coupler options

`IPCCouplerOptions` exposes the Genesis-side coupling behavior plus pass-through knobs for the libuipc solver. Most solver knobs default to `None`, meaning libuipc's own default applies; the fields below are the ones you are most likely to set. See the {doc}`IPCCoupler options API </api_reference/engine/couplers/ipc_coupler>` for the complete list, including the Newton, line-search, and linear-system parameters.

| Parameter | Default | Description |
|---|---|---|
| `contact_d_hat` | `None` (libuipc: 0.01) | Contact barrier distance in meters. Size it to the mesh resolution. |
| `contact_enable` | `None` (libuipc: `True`) | Whether contact detection is active. |
| `contact_friction_enable` | `None` (libuipc: `True`) | Whether contact applies friction. Per-body friction comes from the material (`coup_friction` for rigid, `friction_mu` for FEM). |
| `contact_resistance` | `1e9` | Ground and default contact stiffness; the per-entity fallback when a material sets no `contact_resistance`. |
| `constraint_strength_translation` | `100.0` | Stiffness of the position coupling between Genesis rigid bodies and their IPC affine bodies. |
| `constraint_strength_rotation` | `100.0` | Stiffness of the orientation coupling. Higher is stiffer but can destabilize. |
| `two_way_coupling` | `True` | Whether IPC forces and torques act back on Genesis rigid bodies. Set `False` for one-way coupling. |
| `enable_rigid_ground_contact` | `True` | Whether IPC bodies collide with the ground plane. Disable to avoid double-counting ground contact already handled by Genesis. |
| `enable_rigid_rigid_contact` | `True` | Whether IPC detects contact between rigid (ABD) bodies. Disable to keep only soft-soft and soft-rigid contact. |

Friction is a per-material property, not a coupler-wide setting: set `coup_friction` on a {py:class}`gs.materials.Rigid <genesis.engine.materials.rigid.Rigid>` and `friction_mu` on an FEM material.

## Robot grasping

The complete script is [`examples/IPC_Solver/ipc_robot_grasp_cube.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/IPC_Solver/ipc_robot_grasp_cube.py): a Franka arm grasps and lifts a deformable cube. Here IPC couples only the fingers, while the deformable cube is an FEM solid:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),
    coupler_options=gs.options.IPCCouplerOptions(
        constraint_strength_translation=10.0,
        constraint_strength_rotation=10.0,
        enable_rigid_rigid_contact=False,  # only finger-cube contact matters here
        enable_rigid_ground_contact=False,
    ),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda_non_overlap.xml"),
    material=gs.materials.Rigid(
        coup_type="two_way_soft_constraint",
        coup_links=("left_finger", "right_finger"),
        coup_friction=0.8,
    ),
)

cube = scene.add_entity(
    morph=gs.morphs.Box(pos=(0.65, 0.0, 0.03), size=(0.05, 0.05, 0.05)),
    material=gs.materials.FEM.Elastic(
        E=5.0e4,  # Young's modulus (Pa)
        nu=0.45,
        rho=1000.0,
        friction_mu=0.5,
        model="stable_neohookean",
    ),
)
```

For an interactive version you can teleoperate from the keyboard, see [`examples/IPC_Solver/ipc_robot_cloth_teleop.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/IPC_Solver/ipc_robot_cloth_teleop.py).

## See also

- {doc}`Couplers overview <index>`: how to choose between the legacy, SAP, and IPC couplers.
- {doc}`SAP coupler <sap_coupler>`: the semi-analytic alternative for rigid-FEM contact.
- {doc}`Non-rigid models </user_guide/theory/nonrigid_models>`: FEM, cloth, and other deformable materials.
