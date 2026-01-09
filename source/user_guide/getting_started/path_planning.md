# 🗺️ Path Planning

Genesis provides RRT-based motion planning for collision-free robot paths.

## Basic Usage

```python
import genesis as gs
import numpy as np

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
obstacle = scene.add_entity(gs.morphs.Box(pos=(0.5, 0, 0.3), size=(0.1, 0.3, 0.3), fixed=True))
scene.build()

# Define goal configuration
goal_qpos = robot.inverse_kinematics(
    link=robot.get_link("hand"),
    pos=np.array([0.6, 0.0, 0.3]),
)

# Plan collision-free path
path = robot.plan_path(qpos_goal=goal_qpos, num_waypoints=200)

# Execute path
for waypoint in path:
    robot.control_dofs_position(waypoint)
    scene.step()
```

## Parameters

```python
robot.plan_path(
    qpos_goal,                  # Goal configuration (required)
    qpos_start=None,            # Start config (default: current)
    planner="RRTConnect",       # "RRT" or "RRTConnect"
    num_waypoints=300,          # Output path length
    resolution=0.05,            # Planning resolution
    smooth_path=True,           # Apply path smoothing
    max_nodes=4000,             # Max tree size
    timeout=None,               # Timeout per attempt (seconds)
    max_retry=1,                # Retry count
    ignore_collision=False,     # Skip collision checks
)
```

## Planner Types

- **RRTConnect** (default): Bidirectional, more efficient
- **RRT**: Single-tree, simpler

## Planning with Object Attachment

Plan while carrying an object:

```python
path = robot.plan_path(
    qpos_goal=target_qpos,
    ee_link_name="hand",
    with_entity=cube,
)
```

## Check Planning Success

```python
path, is_valid = robot.plan_path(
    qpos_goal=target_qpos,
    return_valid_mask=True,
)

if is_valid:
    print("Planning succeeded!")
```

## Multi-Environment Planning

```python
scene.build(n_envs=16)

# Plan for all environments
path = robot.plan_path(qpos_goal=target_qpos)
print(path.shape)  # (num_waypoints, 16, n_dofs)

# Plan for specific environments
path, valid = robot.plan_path(
    qpos_goal=target_qpos,
    envs_idx=[0, 5, 10],
    return_valid_mask=True,
)
```

## Performance Tips

- Increase `resolution` for faster (lower quality) planning
- Decrease `resolution` for smoother paths
- Use `timeout` and `max_retry` for reliability
- `RRTConnect` is generally faster than `RRT`
