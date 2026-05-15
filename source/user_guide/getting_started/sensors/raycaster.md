# 📡 Raycaster Sensors

The `Raycaster` family measures distance by casting rays into the scene and detecting intersections with geometry. Concrete sensors are `Lidar` (returns the full ray hit set) and `DepthCamera` (returns the hits formatted as a depth image). The number of rays and their directions are controlled by a `RaycastPattern`.

## Lidar and DepthCamera

```python
lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.SphericalPattern(),
        entity_idx=robot.idx,        # attach to a rigid entity
        pos_offset=(0.3, 0.0, 0.1),  # offset from attached entity
        return_world_frame=True,     # return points in world frame (else local frame)
    )
)

depth_camera = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=gs.sensors.DepthCameraPattern(
            res=(480, 360),          # image resolution (width, height)
            fov_horizontal=90,       # field of view in degrees
            fov_vertical=40,
        ),
    )
)

scene.build()
scene.step()

lidar.read()                # NamedTuple(points=..., distances=...)
depth_camera.read_image()   # tensor (height, width) of distances
```

The example script at `examples/sensors/lidar_teleop.py` demonstrates a raycaster sensor mounted on a robot. Set `--pattern` to `spherical` for a Lidar-like pattern, `grid` for a planar grid pattern, or `depth` for a depth camera.

Running `python examples/sensors/lidar_teleop.py --pattern depth`:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/depth_camera.mp4" type="video/mp4">
</video>

## Common options

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

## Patterns

| Pattern | Use case |
|---|---|
| `SphericalPattern` | 3D LiDAR (Velodyne, Ouster) |
| `DepthCameraPattern` | Depth cameras (RealSense, Kinect) |
| `GridPattern` | Planar sensing, height maps |

### SphericalPattern (LiDAR)

```python
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

Parameters:

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),               # (horizontal, vertical) degrees
    n_points=(128, 64),              # (horizontal, vertical) rays
    angular_resolution=(0.25, 0.5),  # alternative: degrees per ray
    angles=(h_angles, v_angles),     # custom angle arrays
)
```

Real-world LiDAR configurations:

```python
# Velodyne VLP-16
velodyne = gs.sensors.SphericalPattern(fov=(360.0, 30.0), n_points=(1800, 16))

# Front-facing 120° FOV
front_lidar = gs.sensors.SphericalPattern(fov=((-60, 60), 30.0), n_points=(128, 32))
```

### DepthCameraPattern

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

Parameters:

```python
gs.sensors.DepthCameraPattern(
    res=(640, 480),         # resolution (width, height)
    fov_horizontal=90.0,    # horizontal FOV degrees
    fov_vertical=None,      # auto-computed from aspect ratio
    fx=None, fy=None,       # focal lengths (override FOV)
    cx=None, cy=None,       # principal point
)
```

### GridPattern

Planar grid of parallel rays:

```python
pattern = gs.sensors.GridPattern(
    resolution=0.1,             # 10 cm spacing
    size=(2.0, 2.0),            # 2 m x 2 m grid
    direction=(0.0, 0.0, -1.0), # pointing down
)
```

## Reading data

```python
data = lidar.read()
points = data.points         # shape: (n_h, n_v, 3)
distances = data.distances   # shape: (n_h, n_v)

depth_image = depth_cam.read_image()  # shape: (H, W)
```

## Multi-environment

```python
scene.build(n_envs=4)
data = lidar.read()
print(data.points.shape)  # (4, n_h, n_v, 3)
```
