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

    # Get raycast data (RaycasterReturnType NamedTuple)
    data = lidar.read()
    print(f"Min distance: {data.distances.min():.2f} m")
```

## Output Format

`read()` returns a `RaycasterReturnType` NamedTuple:

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
            fov=(360.0, 30.0),  # (horizontal, vertical) field of view, degrees
        ),
        entity_idx=robot.idx,
    )
)
```

### Custom Pattern

There is no `ray_directions` argument on `Raycaster`. To cast an arbitrary set of rays, subclass `gs.sensors.RaycastPattern` and fill in `_ray_dirs` (unit direction vectors in the sensor frame), then pass an instance as `pattern`.

```python
import torch
import genesis as gs

class CrossPattern(gs.sensors.RaycastPattern):
    def _get_return_shape(self):
        return (4,)

    def compute_ray_dirs(self):
        self._ray_dirs[:] = torch.tensor(
            [
                [1.0, 0.0, 0.0],   # forward
                [0.0, 1.0, 0.0],   # left
                [-1.0, 0.0, 0.0],  # back
                [0.0, -1.0, 0.0],  # right
            ],
            dtype=gs.tc_float,
            device=gs.device,
        )

sensor = scene.add_sensor(
    gs.sensors.Raycaster(
        pattern=CrossPattern(),
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
.. autoclass:: genesis.engine.sensors.raycaster.RaycasterSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`index` - Sensor overview
- {doc}`camera` - Visual sensing
