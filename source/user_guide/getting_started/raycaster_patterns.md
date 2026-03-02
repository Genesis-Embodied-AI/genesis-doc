# 📡 Raycaster Patterns

Genesis provides multiple ray patterns for LiDAR and depth sensor simulation.

## Pattern Types

| Pattern | Use Case |
|---------|----------|
| `SphericalPattern` | 3D LiDAR (Velodyne, Ouster) |
| `DepthCameraPattern` | Depth cameras (RealSense, Kinect) |
| `GridPattern` | Planar sensing, height maps |

## SphericalPattern (LiDAR)

```python
import genesis as gs

# 360° horizontal, 60° vertical FOV
pattern = gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),
    n_points=(128, 32),
)

lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.15),
        max_range=100.0,
        min_range=0.1,
        draw_debug=True,
    )
)
```

### SphericalPattern Parameters

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),              # (horizontal, vertical) degrees
    n_points=(128, 64),             # (horizontal, vertical) rays
    angular_resolution=(0.25, 0.5), # Alternative: degrees per ray
    angles=(h_angles, v_angles),    # Custom angle arrays
)
```

### Real LiDAR Configurations

```python
# Velodyne VLP-16
velodyne = gs.sensors.SphericalPattern(fov=(360.0, 30.0), n_points=(1800, 16))

# Front-facing 120° FOV
front_lidar = gs.sensors.SphericalPattern(fov=((-60, 60), 30.0), n_points=(128, 32))
```

## DepthCameraPattern

```python
pattern = gs.sensors.DepthCameraPattern(
    res=(640, 480),
    fov_horizontal=87.0,
)

depth_cam = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=pattern,
        entity_idx=robot.idx,
        pos_offset=(0.0, 0.0, 0.05),
        max_range=5.0,
    )
)
```

### DepthCameraPattern Parameters

```python
gs.sensors.DepthCameraPattern(
    res=(640, 480),           # Resolution (width, height)
    fov_horizontal=90.0,      # Horizontal FOV degrees
    fov_vertical=None,        # Auto-computed from aspect ratio
    fx=None, fy=None,         # Focal lengths (override FOV)
    cx=None, cy=None,         # Principal point
)
```

## GridPattern

Planar grid of parallel rays:

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,            # 10cm spacing
    size=(2.0, 2.0),           # 2m x 2m grid
    direction=(0.0, 0.0, -1.0), # Pointing down
)
```

## Reading Sensor Data

```python
scene.build()
scene.step()

# LiDAR data
data = lidar.read()
points = data.points         # Shape: (n_h, n_v, 3)
distances = data.distances   # Shape: (n_h, n_v)

# Depth camera image
depth_image = depth_cam.read_image()  # Shape: (H, W)
```

## Common Options

```python
gs.sensors.Lidar(
    pattern=pattern,
    entity_idx=robot.idx,
    pos_offset=(0.0, 0.0, 0.15),
    euler_offset=(0.0, 0.0, 0.0),
    max_range=100.0,
    min_range=0.1,
    return_world_frame=True,
    draw_debug=True,
)
```

## Multi-Environment

```python
scene.build(n_envs=4)
data = lidar.read()
print(data.points.shape)  # (4, n_h, n_v, 3) for batched envs
```
