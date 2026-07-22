# Rigid bodies

A rigid body is the default kind of entity in Genesis World: a solid that does not deform, simulated by the rigid solver. It is what you get from {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>`, and it covers most of robotics, robot arms, grippers, mobile bases, and the props they interact with. This page is the overview of that entity type; the rest of this section covers the non-rigid families that build on the same `Scene`.

## Adding a rigid body

An entity is rigid whenever its `material` is `gs.materials.Rigid`, which is the default, so you usually pass only a {doc}`morph </user_guide/assets/loading_assets>`:

```python
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5), size=(0.2, 0.2, 0.2)))
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))
```

Both are rigid entities. The box is a single body; the Franka is **articulated**, a tree of rigid **links** connected by **joints**.

## Single bodies and articulated bodies

Every rigid entity is a `RigidEntity`, and you interact with it through its own methods rather than a global handle. An articulated entity exposes its structure:

- **Links** (`entity.links`, `entity.n_links`): the individual rigid bodies in the tree.
- **Joints** (`entity.joints`, `entity.n_joints`): the connections between links.
- **Degrees of freedom** (`entity.n_dofs`): the independent coordinates the joints move along. A single free body has 6 dofs; a fixed box has none.

You read and write state through the entity: `get_pos()` and `get_quat()` for the base pose, and `get_dofs_position()` for joint positions. Driving those dofs with a controller is covered in {doc}`Control your robot </user_guide/getting_started/control_your_robot>` and, for arms, {doc}`Robot control </user_guide/robot_control/inverse_kinematics_motion_planning>`.

## Fixed and free bases

Whether an entity's base is bolted to the world or floats freely depends on the morph. An MJCF file specifies the base joint itself; a URDF base is free (a 6-dof joint to the world) unless you pass `fixed=True`. See {doc}`Loading assets </user_guide/assets/loading_assets>` for the details.

## Physical properties

The rigid material sets how a body interacts physically. Pass a configured `gs.materials.Rigid` to override the defaults:

```python
box = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5), size=(0.2, 0.2, 0.2)),
    material=gs.materials.Rigid(
        rho=1000.0,               # density in kg/m3, used to estimate mass
        friction=1.0,             # sliding (Coulomb) friction coefficient
        friction_torsional=0.005, # resists spin about the contact normal (meters)
        friction_rolling=0.0001,  # resists rolling about the tangent axes (meters)
    ),
)
```

Torsional and rolling friction stay inert until enabled on the solver, since they add constraint rows to every contact:

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        friction_cone=gs.friction_cone.elliptic,  # exact isotropic cone (default: pyramidal)
        enable_torsional_friction=True,
        enable_rolling_friction=True,              # requires enable_torsional_friction
    ),
)
```

Reach for the elliptic `friction_cone` when resting objects must stay put instead of slowly creeping. Contact, collision geometry, and constraints, how these bodies actually push on each other, are governed by the rigid solver and documented under {doc}`Theory and modelling </user_guide/theory/rigid_collision/index>`.

## See also

- {doc}`/user_guide/getting_started/control_your_robot`: driving a rigid robot with the built-in controller.
- {doc}`/user_guide/robot_control/inverse_kinematics_motion_planning`: inverse kinematics and collision-free planning.
- {doc}`beyond_rigid_bodies`: the non-rigid solvers (MPM, FEM, PBD, SPH) that share the scene.
- {doc}`/user_guide/theory/rigid_collision/index`: the contact and constraint model behind rigid dynamics.
