# Raycaster Sensor

The `RaycasterSensor` provides ray-based distance measurements, useful for LIDAR simulation, proximity sensing, and obstacle detection.

## Overview

The Raycaster sensor:

- Casts rays from a link's frame into the scene
- Returns hit points and distances to intersecting geometry
- Supports configurable ray patterns (spherical, grid, custom)
- Efficiently uses GPU-accelerated BVH traversal

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.add_entity(gs.morphs.Box(pos=(2, 0, 0.5), size=(1.0, 1.0, 1.0)))  # Obstacle

# Add raycaster sensor (using Lidar options)
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.SphericalPattern(),
        entity_idx=robot.idx,
        pos_offset=(0.3, 0.0, 0.1),
        return_world_frame=True,
    )
)

scene.build()

# Simulation loop
for i in range(100):
    scene.step()

    # Get raycast data (RaycasterData NamedTuple)
    data = lidar.read()
    print(f"Min distance: {data.distances.min():.2f} m")
```

## Output Format

`read()` returns a `RaycasterData` NamedTuple:

| Field | Type | Shape | Description |
|-------|------|-------|-------------|
| `points` | `torch.Tensor` (float32) | `([n_envs,] *pattern_shape, 3)` | Intersection points in world or local frame |
| `distances` | `torch.Tensor` (float32) | `([n_envs,] *pattern_shape)` | Distance to intersection (`max_range` if no hit) |

The `pattern_shape` depends on the ray pattern (e.g. `(n_horizontal, n_vertical)` for spherical, `(height, width)` for depth camera).

## Ray Patterns

### Circular (2D LIDAR)

```python
lidar_2d = scene.add_sensor(
    gs.sensors.Raycaster(
        pattern=gs.sensors.SphericalPattern(),
        entity_idx=robot.idx,
    )
)
```

### Planar (3D LIDAR)

```python
lidar_3d = scene.add_sensor(
    gs.sensors.Raycaster(
        pattern=gs.sensors.SphericalPattern(
            fov_horizontal=360.0,
            fov_vertical=30.0,
        ),
        entity_idx=robot.idx,
    )
)
```

### Custom Pattern

```python
import numpy as np

# Define custom ray directions
rays = np.array([
    [1, 0, 0],    # Forward
    [0, 1, 0],    # Left
    [-1, 0, 0],   # Back
    [0, -1, 0],   # Right
])

sensor = scene.add_sensor(
    gs.sensors.Raycaster(
        ray_directions=rays,
        entity_idx=robot.idx,
    )
)
```

## Performance

The Raycaster uses a GPU-accelerated Linear BVH (LBVH) for efficient ray-scene intersection:

- Scales well with scene complexity
- Efficient for hundreds to thousands of rays
- Batched across parallel environments

## API Reference

```{eval-rst}
.. autoclass:: genesis.engine.sensors.RaycasterSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Sensor overview
- {doc}`camera` - Visual sensing
