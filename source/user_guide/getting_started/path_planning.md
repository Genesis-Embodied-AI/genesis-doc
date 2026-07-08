# Path planning

`plan_path` finds a collision-free trajectory through a robot's joint space, from its current configuration to a goal configuration. It is a kinematic planner: it reasons about which joint angles collide with the scene, not about forces or dynamics. The result is a list of waypoints you then execute with the controller of your choice.

This page covers `plan_path` on its own. For the full pick-and-place workflow that pairs it with inverse kinematics and gripper control, see {doc}`inverse_kinematics_motion_planning`, whose runnable script ([`examples/tutorials/IK_motion_planning_grasp.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/IK_motion_planning_grasp.py)) is the source of truth for the excerpts below.

## Mental model

Planning happens in **configuration space**: a point is a full joint configuration (`qpos`), not a Cartesian pose. You give the planner a goal `qpos`, and it searches for a sequence of configurations that connects the start to the goal without any of them putting the robot in collision.

Two consequences follow from this, and both are common sources of confusion:

- **You usually need inverse kinematics first.** A task is normally stated as an end-effector pose in the world, but the planner wants a joint configuration. {doc}`inverse_kinematics_motion_planning` converts one to the other; feed its `qpos` output in as `qpos_goal`.
- **Planning does not move the robot.** `plan_path` returns waypoints; it does not step the simulation. The robot only moves when you send those waypoints to a controller and call `scene.step()`.

The planners are sampling-based (RRT and RRTConnect). They are probabilistically complete (given enough time they find a path if one exists), but they are randomized, so two runs on the same problem can return different paths, and a hard problem can fail within the retry budget.

## Minimal example

Solve IK for a goal pose, plan a path to that configuration, then drive the robot along it:

```python
end_effector = franka.get_link("hand")

qpos_goal = franka.inverse_kinematics(
    link=end_effector,
    pos=np.array([0.65, 0.0, 0.25]),  # world-frame target, meters, Z-up
    quat=np.array([0, 1, 0, 0]),  # w-x-y-z; gripper points down
)

path = franka.plan_path(
    qpos_goal=qpos_goal,
    num_waypoints=200,  # 200 steps at dt=0.01 s -> 2 s of motion
)

for waypoint in path:
    franka.control_dofs_position(waypoint)
    scene.step()
```

`num_waypoints` sets how finely the found path is resampled, one waypoint per simulation step, so `num_waypoints * dt` is the wall-clock duration of the motion. Waypoints are full `qpos` vectors of shape `(num_waypoints, n_qs)` for a single environment.

:::{tip}
Let the controller settle after the last waypoint. Position control is a PD controller, so the arm trails its commanded target by a small error; stepping a little longer lets it converge before the next phase begins.

```python
for i in range(100):
    scene.step()
```
:::

You can preview a planned path in the viewer before executing it:

```python
path_debug = scene.draw_debug_path(path, franka)  # renders the trajectory
# ... execute the path ...
scene.clear_debug_object(path_debug)  # remove it afterward
```

## Planners and parameters

`plan_path` exposes two sampling-based planners, selected with `planner`:

| Planner | Description |
|---|---|
| `"RRTConnect"` (default) | Grows two trees, from the start and the goal, and connects them. Usually faster. |
| `"RRT"` | Grows a single tree from the start. Simpler, generally slower to connect. |

The remaining arguments control the search and the output:

| Argument | Default | Meaning |
|---|---|---|
| `qpos_goal` | (required) | Goal configuration. |
| `qpos_start` | `None` | Start configuration; `None` uses the robot's current `qpos`. |
| `resolution` | `0.05` | Joint-space step, in radians, at which segments are checked for collision. Smaller catches thinner obstacles at higher cost. |
| `max_nodes` | `2000` | Cap on the search tree size before a single attempt gives up. |
| `timeout` | `None` | Wall-clock budget per attempt, in seconds (approximate). |
| `max_retry` | `1` | Extra attempts after the first if planning fails. |
| `smooth_path` | `True` | Shortcut-smooth the raw path before resampling. |
| `num_waypoints` | `300` | Number of waypoints to resample the path to. `None` skips interpolation. |
| `ignore_collision` | `False` | Skip all collision checks. |

:::{warning}
`resolution` sets how far apart two configurations may be before the segment between them is treated as collision-checked. If it is larger than the thinnest obstacle in configuration space, the planner can step over a collision and return a path that clips through geometry. Reduce it when paths look valid but pass through obstacles.
:::

## Planning while carrying an object

When the robot has grasped an object, that object becomes part of the swept volume and must be checked for collision too. Attach it for the duration of the plan by naming the gripper link and passing the entity:

```python
path = franka.plan_path(
    qpos_goal=place_qpos,
    ee_link_name="hand",  # link the object is rigidly attached to
    with_entity=cube,
)
```

The attachment is used only while planning; it does not create a physical constraint. Only a single non-articulated entity is supported. To weld links together in the simulation itself, see {doc}`constraints`.

## Checking whether planning succeeded

Set `return_valid_mask=True` to get a success flag alongside the path. For a single environment it is a scalar boolean:

```python
path, is_valid = franka.plan_path(qpos_goal=qpos_goal, return_valid_mask=True)
if not is_valid:
    print("no collision-free path found within the retry budget")
```

When the mask is not requested, a failed plan still returns a path-shaped tensor. Check the flag rather than assuming the waypoints are usable.

## Planning across parallel environments

In a {doc}`batched scene <parallel_simulation>`, `plan_path` plans for every environment at once. The returned tensor gains a leading environment dimension:

```python
scene.build(n_envs=16)

path = franka.plan_path(qpos_goal=qpos_goal)
print(path.shape)  # (num_waypoints, n_envs, n_qs)
```

Pass `envs_idx` to plan for a subset; the environment dimension of the result then matches the number of indices. Combine it with `return_valid_mask` to see which environments succeeded, since randomized planning may solve some and not others:

```python
path, valid = franka.plan_path(
    qpos_goal=qpos_goal,
    envs_idx=[0, 5, 10],
    return_valid_mask=True,
)  # path: (num_waypoints, 3, n_qs); valid: (3,)
```

## Notes and gotchas

- **Free and spherical joints are unsupported.** The planner rejects entities with a free or spherical joint. A mobile base modeled as a free joint therefore cannot be planned for directly.
- **Planning is randomized.** For reliability on hard problems, give the planner room with `timeout` and `max_retry` rather than expecting the first attempt to succeed.
- **`ignore_collision=True` disables the point of planning.** It produces a straight-line interpolation in joint space and is only useful for a quick trajectory when you already know the space is clear.

## See also

- {doc}`inverse_kinematics_motion_planning`: full pick-and-place: IK, planning, and gripper control together
- {doc}`advanced_ik`: multi-target IK, null-space control, and solver tuning
- {doc}`control_your_robot`: position, velocity, and force control in depth
- {doc}`constraints`: weld and connect constraints for locking links at runtime
