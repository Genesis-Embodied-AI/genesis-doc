# Raycaster sensors

A raycaster measures the scene geometrically: it casts a fixed pattern of rays from the sensor's frame, finds where each ray first hits scene geometry, and returns the hit points and their distances. Two concrete sensors share this machinery and differ only in how you interpret the result:

- `gs.sensors.Lidar` returns the raw hit set (a point cloud and per-ray distances) for range sensing, mapping, and obstacle avoidance.
- {py:class}`gs.sensors.DepthCamera <genesis.options.sensors.options.DepthCamera>` casts a pinhole-camera ray grid and reshapes the distances into a depth image.

The ray count and directions come from a **pattern** ({py:class}`gs.sensors.RaycastPattern <genesis.options.sensors.raycaster.RaycastPattern>`). Two runnable examples are the source of truth for this page: a teleoperated sensor mounted on a Go2 in [`examples/sensors/lidar_teleop.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/lidar_teleop.py), and depth cameras on rigid and deforming geometry in [`examples/sensors/depth_camera_custom_vverts.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/depth_camera_custom_vverts.py).

## Minimal example

Mount a spinning lidar on a robot, add something for the rays to hit, and read the point cloud each step:

```python
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(show_viewer=True)
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf", fixed=True))
scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 1.0), pos=(2.0, 0.0, 0.5), fixed=True))

lidar = scene.add_sensor(
    gs.sensors.Lidar(
        pattern=gs.sensors.SphericalPattern(),  # 360deg x 60deg fov, 128 x 64 rays
        entity_idx=robot.idx,                   # mount on the robot's base link
        pos_offset=(0.3, 0.0, 0.1),             # meters, in the link frame
        max_range=20.0,                         # meters
        return_world_frame=True,
        draw_debug=True,                        # draw hit points in the viewer
    )
)

scene.build()
for _ in range(1000):
    scene.step()
    result = lidar.read()          # RaycasterReturnType(points, distances)
    points = result.points         # shape (128, 64, 3), meters, Z-up world frame
    distances = result.distances   # shape (128, 64), meters
```

The lidar needs geometry to cast against: a raycaster raises at build time if the rigid solver is inactive and no entity opts into visual raycasting.

## How ray casting works

A pattern is a purely local description of the rays: it fixes a start point and a unit direction for each ray in the sensor's own frame, independent of where the sensor ends up in the world. The pattern's `return_shape` (for example `(n_horizontal, n_vertical)` for a spherical scan) sets the layout every read preserves.

At each `read()`, Genesis World places the pattern in the world by composing the attached link's pose with the sensor's `pos_offset` and `euler_offset`, then casts every ray against an acceleration structure built over the scene's geometry. Each ray reports the first surface it hits. A ray that hits nothing within `max_range`, or closer than `min_range`, reports `no_hit_value` (which defaults to `max_range`) so the returned tensors keep a fixed shape.

Attach a sensor to a link by setting `entity_idx` and `link_idx_local`; the rays then move with that link. Leave `entity_idx` unset (or `None`) for a world-fixed sensor, in which case `pos_offset` and `euler_offset` are applied in the world frame.

## Reading data

`read()` returns a {py:class}`RaycasterReturnType <genesis.engine.sensors.raycaster.RaycasterReturnType>`, a `NamedTuple` of `points` and `distances`:

```python
result = lidar.read()
points = result.points        # shape ([n_envs,] *return_shape, 3), meters
distances = result.distances  # shape ([n_envs,] *return_shape),    meters
```

- **`distances`** is the along-ray hit distance in meters, with misses filled by `no_hit_value`.
- **`points`** is the hit location per ray. With `return_world_frame=True` it is in the world frame (Z-up, meters); with the default `return_world_frame=False` it is in the sensor's local frame.
- **`return_points=False`** measures the hit distances only: `read().points` is `None`, and the sensor's memory and per-step cost drop to about a quarter. Use it for distance-only sensing (e.g. depth images); keep the default `True` when you need the point cloud.

The `return_shape` is set by the pattern, so the trailing axes match the pattern's own layout: `(128, 64)` for the default spherical scan, `(height, width)` for a depth camera, `(n_x, n_y)` for a grid. The leading `[n_envs,]` axis is present only when the scene is built with multiple environments (see [Multiple environments](#multiple-environments)).

## Ray patterns

The pattern decides what the sensor is. All three are constructed under `gs.sensors` and passed as the `pattern` argument.

| Pattern | Ray layout | Typical hardware |
|---|---|---|
| {py:class}`SphericalPattern <genesis.options.sensors.raycaster.SphericalPattern>` | azimuth × elevation scan lines | 3D lidar (Velodyne, Ouster) |
| {py:class}`DepthCameraPattern <genesis.options.sensors.raycaster.DepthCameraPattern>` | pinhole image grid | depth cameras (RealSense, Kinect) |
| {py:class}`GridPattern <genesis.options.sensors.raycaster.GridPattern>` | parallel rays on a plane | height maps, planar sensing |

### SphericalPattern

Rays fan out over a horizontal (azimuth) and vertical (elevation) field of view. Specify the pattern by ray count, by angular resolution, or by explicit angle arrays:

```python
gs.sensors.SphericalPattern(
    fov=(360.0, 60.0),   # (horizontal, vertical) degrees; a scalar is centered on 0deg,
                         # a (min, max) tuple gives an asymmetric range
    n_points=(128, 64),  # (horizontal, vertical) ray counts -> return_shape (128, 64)
    # angular_resolution=(0.25, 0.5),  # degrees per ray; overrides n_points
    # angles=(h_angles, v_angles),     # explicit angle arrays; overrides the rest
)
```

**First mention of SphericalPattern:**

To model a real unit, set the fov and ray counts from its datasheet. For example, a Velodyne VLP-16 is `fov=(360.0, 30.0), n_points=(1800, 16)`.

### DepthCameraPattern

A pinhole camera whose optical axis is the sensor's local **+X** axis. Configure it by field of view or by explicit intrinsics:

```python
gs.sensors.DepthCameraPattern(
    res=(128, 96),        # (width, height) in pixels -> return_shape (96, 128)
    fov_horizontal=90.0,  # degrees; fov_vertical is derived from the aspect ratio
    # fov_vertical=None,  # set instead to derive fov_horizontal, or set both
    # fx=None, fy=None,   # focal lengths in pixels, override the fov
    # cx=None, cy=None,   # principal point in pixels, defaults to the image center
)
```

### GridPattern

Parallel rays cast from a plane in a single direction, a height map under the sensor, for instance:

```python
gs.sensors.GridPattern(
    resolution=0.1,              # grid spacing, meters (>= 1 mm)
    size=(2.0, 2.0),             # (length, width) of the grid, meters
    direction=(0.0, 0.0, -1.0),  # ray direction in the sensor frame (here: straight down)
)
```

### Custom pattern

There is no `ray_directions` argument. To cast an arbitrary set of rays, subclass `gs.sensors.RaycastPattern`: return the layout shape from `_get_return_shape()` and fill `_ray_dirs` (unit directions in the sensor frame) in `compute_ray_dirs()`.

```python
import torch

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

sensor = scene.add_sensor(gs.sensors.Lidar(pattern=CrossPattern(), entity_idx=robot.idx))
```

## Depth cameras

`gs.sensors.DepthCamera` is a raycaster with a `DepthCameraPattern`. It exposes everything a lidar does, plus `read_image()`, which reshapes the per-ray distances into a depth image:

```python
depth_cam = scene.add_sensor(
    gs.sensors.DepthCamera(
        pattern=gs.sensors.DepthCameraPattern(
            res=(96, 72),         # (width, height) in pixels
            fov_horizontal=90.0,  # degrees
        ),
        entity_idx=go2.idx,
        link_idx_local=0,
        pos_offset=(0.3, 0.0, 0.1),  # meters, in the link frame
        max_range=5.0,               # meters
        return_world_frame=True,
    ),
)

scene.build()
scene.step()
depth = depth_cam.read_image()  # shape ([n_envs,] 72, 96), meters
```

`read_image()` returns the `distances` field alone, reshaped to `([n_envs,] height, width)`; misses carry `no_hit_value`. The point cloud is still available through `read().points`, unless the camera is created with `return_points=False`, which skips it to save memory when only depth is needed. Because a depth camera shares the raycasting backend with any lidar in the scene, the two cast against the same geometry.

Running `python examples/sensors/lidar_teleop.py --pattern depth` teleoperates a depth camera on the Go2 (`--pattern` also accepts `spherical` and `grid`):

<video preload="auto" controls="True" width="100%" alt="Depth image from a camera sensor mounted on a Go2 robot walking among obstacles">
<source src="../../_static/videos/depth_camera.mp4" type="video/mp4">
</video>

## Common options

`Lidar` and `DepthCamera` share the raycaster options below (the mounting fields are common to all attached sensors):

```python
gs.sensors.Lidar(
    pattern=pattern,
    entity_idx=robot.idx,        # attach to this entity; omit for a world-fixed sensor
    link_idx_local=0,            # which link of the entity to attach to
    pos_offset=(0.0, 0.0, 0.15), # meters, in the link frame
    euler_offset=(0.0, 0.0, 0.0),# extrinsic x-y-z, degrees
    min_range=0.0,               # meters; hits closer than this are dropped
    max_range=20.0,              # meters
    no_hit_value=None,           # value for a miss; defaults to max_range
    return_world_frame=False,    # world frame if True, else the sensor's local frame
    return_points=True,          # False measures distances only; read().points is then None
    draw_debug=False,            # draw ray starts and hit points in the viewer
)
```

## Multiple environments

Build with `n_envs > 0` and every read gains a leading batch axis; the pattern layout is unchanged:

```python
scene.build(n_envs=4)
scene.step()
result = lidar.read()
result.points.shape     # (4, 128, 64, 3)
result.distances.shape  # (4, 128, 64)
```

## See also

- {doc}`Sensors overview <index>`: the sensor pipeline, noise, delay, and batched reads.
- {doc}`Camera sensors <camera_sensors>`: rendered RGB, depth, and segmentation through a camera.
- {doc}`Recording data </user_guide/sensing/recorders>`: save depth images and point clouds alongside the simulation.
- {doc}`Conventions </user_guide/configuration/conventions>`: the Z-up frame and unit conventions the returned points follow.
