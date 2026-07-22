# Hybrid entities

A hybrid entity couples a rigid skeleton to a soft skin so that the two simulate as one body. The rigid part carries the joints you control; the soft part deforms around it and pushes back through contact. Use it for compliant manipulators, soft grippers, and creatures whose motion comes from a jointed frame but whose surface is deformable.

The complete script is [`examples/tutorials/advanced_hybrid_robot.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/advanced_hybrid_robot.py): a two-link arm with a soft skin that sweeps a rigid ball across the ground.

## Mental model

A hybrid entity is not a single solver's object. Genesis World builds it from two entities that share the same scene and timestep:

- A **rigid part** (a {py:class}`RigidEntity <genesis.engine.entities.rigid_entity.rigid_entity.RigidEntity>`) parsed from the URDF, carrying the joints and **degrees of freedom** (**dofs**).
- A **soft part** (an {py:class}`MPMEntity <genesis.engine.entities.mpm_entity.MPMEntity>`) whose particles are attached to the rigid links.

Each simulation step, the rigid solver advances the joints, and the coupling maps every soft particle back onto the link it belongs to; the particles' reaction then feeds a force back onto the rigid link. You drive the entity through the rigid dofs; the skin follows. The soft material must be MPM-based; FEM and PBD skins are not yet supported.

## Minimal setup

A hybrid scene needs three things the earlier tutorials did not: an MPM domain, a soft-enough rigid contact solver, and a hybrid material.

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=3e-3,  # s; small for rigid-body numerical stability
        substeps=10,
    ),
    rigid_options=gs.options.RigidOptions(
        gravity=(0, 0, -9.8),  # m/s^2, Z-up
        # A stiff rigid contact solver produces large impulses at this small dt.
        constraint_timeconst=0.02,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(0.0, 0.0, -0.2),  # MPM grid must enclose the soft skin
        upper_bound=(1.0, 1.0, 1.0),
        gravity=(0, 0, 0),  # mimic gravity compensation on the skin
        enable_CPIC=True,
    ),
)
```

The MPM solver simulates the skin on a background grid; `lower_bound` and `upper_bound` (meters) define that grid, and anything that leaves it is lost. Keep the entity comfortably inside.

## Add the hybrid entity

Pass a {py:class}`gs.morphs.URDF <genesis.options.morphs.URDF>` for the skeleton and a {py:class}`gs.materials.Hybrid <genesis.engine.materials.hybrid.Hybrid>` that wraps one rigid and one soft material:

```python
robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="urdf/simple/two_link_arm.urdf",
        pos=(0.5, 0.5, 0.3),
        scale=0.2,
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(
            gravity_compensation=1.0,  # cancel gravity on the skeleton
        ),
        material_soft=gs.materials.MPM.Muscle(
            E=1e4,  # Young's modulus, Pa
            nu=0.45,  # Poisson's ratio
            rho=1000.0,  # kg/m^3
            model="neohooken",
        ),
        thickness=0.05,  # m; skin inflated outward from each link's collision mesh
        damping=1000.0,
    ),
)
```

The skin is generated automatically: for each rigid link with a collision geometry, Genesis World inflates that geometry outward by `thickness` (meters) and fills it with MPM particles bound to the link. Gravity on the skin is cancelled by setting the MPM solver's `gravity` to zero above, and on the skeleton by `gravity_compensation=1.0`, so the arm holds its pose instead of sagging.

### Hybrid material parameters

| Parameter | Default | Meaning |
|---|---|---|
| `material_rigid` | required | Material of the rigid skeleton, e.g. {py:class}`gs.materials.Rigid <genesis.engine.materials.rigid.Rigid>`. |
| `material_soft` | required | Material of the soft skin. Must be an `gs.materials.MPM.*` type. |
| `thickness` | `0.05` | Skin thickness in meters, inflated outward from each link's mesh. |
| `damping` | `0.0` | Damps the relative velocity between skin and skeleton; higher values reduce oscillation. |
| `soft_dv_coef` | `0.01` | Fraction of the coupling velocity fed from the skeleton back into the skin. |
| `use_default_coupling` | `False` | Use the solver's built-in coupler instead of the hybrid entity's per-particle coupling. |

## Control

You control a hybrid entity through its rigid dofs, using the same methods as a plain `RigidEntity`. They are forwarded to the rigid part:

```python
for i in range(1000):
    dofs_ctrl = [1.0 * np.sin(2 * np.pi * i * 0.001)] * robot.n_dofs
    robot.control_dofs_velocity(dofs_ctrl)
    scene.step()
```

`control_dofs_position`, `control_dofs_velocity`, `control_dofs_force`, and the matching `get_dofs_position` / `get_dofs_velocity` / `get_dofs_force` all act on the skeleton. The soft skin has no independent controls; it moves because its links move.

## Accessing the parts

The two underlying entities are exposed as properties if you need to read or render them separately:

```python
robot.part_rigid   # the RigidEntity skeleton
robot.part_soft    # the MPMEntity skin
robot.n_dofs       # dofs of the skeleton
```

`solver_rigid` and `solver_soft` return the respective solvers.

## Notes and gotchas

:::{note}
The rigid and soft solvers must share the same `dt`. Genesis World asserts this at construction, so set the timestep once in `sim_options` rather than per solver.
:::

:::{warning}
The MPM grid defined by `lower_bound` / `upper_bound` is finite. Particles that move outside it are dropped, which shows up as skin tearing away from the skeleton. Size the bounds to contain the entity's full range of motion.
:::

:::{tip}
Hybrid dynamics are stiff. If the simulation is unstable, lower `dt`, raise `damping`, or soften the rigid contact solver with a larger `constraint_timeconst` before touching the material stiffness `E`.
:::

A hybrid entity can also be built from a bare {py:class}`gs.morphs.Mesh <genesis.options.morphs.Mesh>`: Genesis World skeletonizes the mesh, builds a rigid body from the extracted skeleton, and binds the soft particles to it. The tested example uses the URDF path shown above; the mesh path is available through the same `gs.materials.Hybrid` material.

## See also

- {doc}`Soft robots <soft_robots>`: muscle actuation for standalone FEM and MPM soft bodies.
- {doc}`Beyond rigid bodies <beyond_rigid_bodies>`: fluids, cloth, and other deformable simulation.
