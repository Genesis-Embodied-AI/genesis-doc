# Rigid-body constraints

A **constraint** ties two rigid links together so the solver keeps a geometric relationship between them: coincident points, a fixed relative pose, or coupled joint values. Most constraints are declared once in a model file and hold for the whole simulation. One kind, the **weld** constraint, can be added and removed while the simulation runs, which is what makes it the tool for modeling a suction gripper picking up and releasing an object.

This page covers the runtime weld API on the rigid solver, and how the file-declared constraint types relate to it.

The complete runnable example is [`examples/rigid/suction_cup.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/suction_cup.py): a Franka arm reaches a cube, welds it to the hand, lifts and moves it, then releases.

## Weld constraints at runtime

A weld constraint pins two links so their relative pose is frozen at the values they have the instant you add it: all six degrees of freedom, translation and rotation. It is the constraint you toggle to model suction or a magnetic gripper: engage it when the end-effector reaches the object, delete it to let go.

The API lives on the rigid solver, not on an entity, because a weld couples links that belong to two different entities. Reach it through `scene.sim.rigid_solver` after the scene is built:

```python
rigid = scene.sim.rigid_solver
link_cube = cube.get_link("box_baselink").idx
link_franka = franka.get_link("hand").idx
rigid.add_weld_constraint(link_cube, link_franka)
```

The arguments are global **link indices** (integers), not link or entity handles. Get an index from a link with `entity.get_link(name).idx`. The order of the two links does not matter.

Deleting the constraint releases the object:

```python
rigid.delete_weld_constraint(link_cube, link_franka)
```

Pass the same two link indices you welded. Once released, the object is governed by contact and gravity again, so it will fall unless something supports it.

:::{note}
A weld records the relative pose at the moment it is added; it does not snap the links together. Move the end-effector into contact with the object *before* welding, or the object will hang in the air at whatever offset it had when the constraint engaged.
:::

## Applying to a subset of environments

In a {doc}`parallel simulation </user_guide/getting_started/parallel_simulation>`, both calls take an `envs_idx` argument to select which environments the weld applies to. Omit it to apply to all environments:

```python
scene.build(n_envs=4)

rigid.add_weld_constraint(link_cube, link_franka, envs_idx=(0, 1, 2))
rigid.delete_weld_constraint(link_cube, link_franka, envs_idx=(0, 1))
```

The two link indices are the same across environments; only the environment selection differs.

## Budgeting for dynamic constraints

Runtime welds draw from a fixed pool sized before the scene is built. The pool holds `max_dynamic_constraints` welds (default 8), set on {py:class}`gs.options.RigidOptions <genesis.options.solvers.RigidOptions>`:

```python
scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(max_dynamic_constraints=16),
)
```

:::{warning}
Adding a weld once the pool is full has no effect: the solver logs a warning and ignores the request rather than raising. If a gripper silently fails to hold its object, check that you have released stale welds and that `max_dynamic_constraints` is large enough for the number held at once.
:::

## Querying active welds

`get_weld_constraints` returns the welds currently active, as a dictionary of tensors keyed by field. `link_a` and `link_b` hold the welded link indices; `force` holds the constraint force. Each is batched over environments, with shape `(n_envs, n_welds_max, ...)`:

```python
welds = rigid.get_weld_constraints()  # dict with keys "link_a", "link_b", "force"
```

Pass `to_torch=False` for NumPy arrays, or `as_tensor=False` to get a per-environment tuple instead of a padded batch.

## Constraint types

Genesis World supports three equality-constraint types. Weld is the only one you add at runtime; the other two are read from a model's `<equality>` block when it is loaded from MJCF or URDF.

| Type | Constrains | Declared in | Runtime API |
|---|---|---|---|
| Connect | A point on each link to coincide (3 DoF), a ball joint. | MJCF | — |
| Weld | Relative pose fully fixed (6 DoF). | MJCF, or `add_weld_constraint` | `add_weld_constraint` / `delete_weld_constraint` |
| Joint | One joint's value tied to another's by a polynomial. | MJCF, URDF | — |

A connect or joint constraint enters the simulation with its host model. There is no runtime API to add or remove it; edit the model file's equality section instead.

## See also

- {doc}`Control your robot </user_guide/getting_started/control_your_robot>`: joint-level position, velocity, and force control.
- {doc}`Inverse kinematics and motion planning <inverse_kinematics_motion_planning>`: the IK solving and path planning the suction example uses to reach the object.
