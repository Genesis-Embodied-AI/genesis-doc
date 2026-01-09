# Raycaster Sensor

The `RaycasterSensor` provides ray-based distance measurements, useful for LIDAR simulation, proximity sensing, and obstacle detection.

## Overview

The Raycaster sensor:

- Casts rays from a link's frame into the scene
- Returns distances to intersecting geometry
- Supports configurable ray patterns (linear, planar, custom)
- Efficiently uses GPU-accelerated BVH traversal

## Usage

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.add_entity(gs.morphs.Box(pos=(2, 0, 0.5)))  # Obstacle
scene.build()

# Add raycaster sensor (using Lidar options)
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        link=robot.get_link("sensor_link"),
    )
)

# Simulation loop
for i in range(100):
    scene.step()

    # Get range data
    ranges = lidar.get_data()  # (n_rays,) array of distances
    print(f"Min range: {ranges.min():.2f} m")
```

## Configuration

```python
gs.sensors.Raycaster(
    link=link,              # RigidLink to attach sensor to
    n_rays=360,             # Number of rays to cast
    min_range=0.1,          # Minimum detection range (m)
    max_range=10.0,         # Maximum detection range (m)
    pattern="circular",     # Ray pattern type

    # Angular range (for circular/linear patterns)
    fov_horizontal=360.0,   # Horizontal field of view (degrees)
    fov_vertical=0.0,       # Vertical field of view (degrees)

    # Position offset from link frame
    offset_pos=(0, 0, 0),
    offset_quat=(0, 0, 0, 1),
)
```

## Ray Patterns

### Circular (2D LIDAR)

```python
lidar_2d = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        n_rays=360,
        pattern="circular",
        fov_horizontal=360.0,
    )
)
```

### Planar (3D LIDAR)

```python
lidar_3d = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        n_rays=16 * 360,  # 16 vertical layers
        pattern="planar",
        fov_horizontal=360.0,
        fov_vertical=30.0,
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

sensor = robot.add_sensor(
    gs.sensors.Raycaster(
        link=base,
        ray_directions=rays,
    )
)
```

## Output Format

| Output | Shape | Description |
|--------|-------|-------------|
| `ranges` | `(n_rays,)` | Distance to intersection (max_range if no hit) |
| `hits` | `(n_rays,)` | Boolean mask of valid intersections |

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
