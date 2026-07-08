# Advanced and parallel IK

The inverse kinematics (IK) solver introduced in {doc}`inverse_kinematics_motion_planning` extends in two directions that matter for real manipulation and for training at scale: solving for several end-effector links at once, and solving every environment of a parallel scene in a single call. This page covers both.

The runnable sources for this page are
[`advanced_IK_multilink.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/advanced_IK_multilink.py)
and
[`batched_IK.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/batched_IK.py).

## IK with multiple end-effector links

A single call to `robot.inverse_kinematics()` positions one link. When a task constrains several links at once (a gripper's two fingertips, both hands of a dual-arm robot, or a closed kinematic loop), solve them jointly with `robot.inverse_kinematics_multilink()`. Solving each link separately would let later solutions undo earlier ones; the multi-link solver finds one joint configuration that satisfies every target together.

The call takes parallel lists: one target link, one position, and one orientation per entry.

```python
left_finger = robot.get_link("left_finger")
right_finger = robot.get_link("right_finger")

q = robot.inverse_kinematics_multilink(
    links=[left_finger, right_finger],
    poss=[target_pos_left, target_pos_right],
    quats=[target_quat, target_quat],
    rot_mask=[False, False, True],  # only restrict direction of z-axis
)
```

Each target need not be a full 6-DoF pose. `pos_mask` and `rot_mask` are length-3 boolean masks that select which position axes and which rotation axes the solver has to satisfy; both default to `[True, True, True]`. Here `rot_mask=[False, False, True]` asks only that each fingertip's z-axis align with the z-axis of `target_quat`, leaving its heading in the horizontal plane free. Masking out constraints you do not care about gives the solver more freedom and makes it more likely to converge.

Orientations follow the `(w, x, y, z)` quaternion convention, so `target_quat = np.array([0, 1, 0, 0])` points the finger's z-axis straight down.

This example is purely kinematic: it demonstrates the solver, not the physics. After solving, it writes the result directly to the robot and refreshes the display rather than stepping the simulation:

```python
# Note that this IK is for visualization purposes, so here we do not call scene.step(), but only update the state and the visualizer
# In actual control applications, you should instead use robot.control_dofs_position() and scene.step()
robot.set_dofs_position(q)
scene.visualizer.update()
```

The target frames in the video are drawn with `scene.draw_debug_frame()` and moved each iteration with `scene.update_debug_objects()`. These markers live at the visualizer level and take no part in the simulation. See {doc}`/user_guide/interaction/interactive_debugging` for the debug-drawing API.

```{video} ../../_static/videos/ik_multilink.mp4
:width: 100%
```

## IK across parallel environments

When a scene is built with multiple environments, the same solver runs across all of them in one call, useful for generating demonstrations or driving policy rollouts without a Python loop over environments. The example spawns 16 environments and rotates each robot's end-effector at a different angular speed.

The only structural change from single-environment IK is the batch dimension. Build the scene with `n_envs`, then give the solver batched targets whose leading dimension is `n_envs`:

```python
n_envs = 16
scene.build(n_envs=n_envs, env_spacing=(1.0, 1.0))

target_quat = np.tile(np.array([0, 1, 0, 0]), [n_envs, 1])  # (n_envs, 4), pointing downwards
center = np.tile(np.array([0.4, -0.2, 0.25]), [n_envs, 1])
angular_speed = np.random.uniform(-10, 10, n_envs)
r = 0.1
ee_link = robot.get_link("hand")
```

Inside the loop, `pos` and `quat` carry the batch dimension and the solver returns one configuration per environment:

```python
target_pos = np.zeros([n_envs, 3])
target_pos[:, 0] = center[:, 0] + np.cos(i / 360 * np.pi * angular_speed) * r
target_pos[:, 1] = center[:, 1] + np.sin(i / 360 * np.pi * angular_speed) * r
target_pos[:, 2] = center[:, 2]

q = robot.inverse_kinematics(
    link=ee_link,
    pos=target_pos,  # shape (n_envs, 3)
    quat=target_quat,  # shape (n_envs, 4)
    rot_mask=[False, False, True],  # for demo purpose: only restrict direction of z-axis
)

robot.set_qpos(q)
scene.step()
```

The returned `q` has shape `([n_envs,] n_dofs)`: batched when the scene has multiple environments, a plain `(n_dofs,)` vector otherwise. The same rule applies to the inputs: `pos` is `([n_envs,] 3)` and `quat` is `([n_envs,] 4)`. The masks stay length-3 and are shared across the batch. `inverse_kinematics_multilink` batches the same way, with each entry of `poss`/`quats` carrying the leading `n_envs` dimension.

```{video} ../../_static/videos/batched_IK.mp4
:width: 100%
```

:::{tip}
Parallel IK is most effective on a GPU backend, where all environments are solved together. See {doc}`/user_guide/getting_started/parallel_simulation` for how batched environments run, and {doc}`/user_guide/getting_started/control_your_robot` for driving the solved configuration through the controllers instead of setting it directly.
:::

## Forward kinematics and the Jacobian

Inverse kinematics is built on two lower-level operations the same solver exposes directly, and both are useful on their own for analytic control. Forward kinematics is IK's inverse: it maps a joint configuration to the resulting link poses. The Jacobian relates joint velocities to the end-effector's spatial velocity, which is the quantity IK differentiates to take each step; it also underpins Jacobian-transpose control and manipulability analysis.

Both require an entity created with `requires_jac_and_IK=True`, which is the default for the `MJCF` and `URDF` robot morphs.

```python
ee_link = robot.get_link("hand")

# Jacobian at the link origin: rows 0-2 are linear, rows 3-5 angular, one column per dof.
jacobian = robot.get_jacobian(link=ee_link)  # shape ([n_envs,] 6, n_dofs)

# Forward kinematics: joint configuration -> world-frame link poses.
qpos = robot.get_qpos()
links_pos, links_quat = robot.forward_kinematics(qpos)
# links_pos:  shape ([n_envs,] n_links, 3)   link-frame origins, world coordinates
# links_quat: shape ([n_envs,] n_links, 4)   orientations, (w, x, y, z)
```

`get_jacobian` takes an optional `local_point` (a length-3 point in the link's local frame) to evaluate the Jacobian somewhere other than the link origin. `forward_kinematics` accepts `qs_idx_local`, `links_idx_local`, and `envs_idx` to compute a subset of the configuration, links, or environments; the returned poses are in the world frame, consistent with the world-frame `qpos` input.

:::{note}
`forward_kinematics` reuses the IK solver's internal buffers, which are allocated the first time you call `inverse_kinematics` on the entity. Solve IK at least once before calling it standalone.
:::
