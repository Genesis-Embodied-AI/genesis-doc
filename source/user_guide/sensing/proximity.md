# Proximity

`gs.sensors.SurfaceDistanceProbe` reports the nearest distance from one or more probe points to the mesh surfaces of a set of tracked rigid links. Each probe is mounted in the local frame of a link and moves with it, so the sensor answers "how close is this point on my robot to those objects?" as the scene evolves.

The complete script is [`examples/sensors/surface_distance_shadowhand.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/surface_distance_shadowhand.py), which mounts probes on the palm and fingertips of a Shadow Hand and measures distance to a duck mesh and a box under keyboard teleoperation.

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="urdf/shadow_hand/shadow_hand.urdf"))
duck = scene.add_entity(
    gs.morphs.Mesh(file="meshes/duck.obj", scale=0.06, pos=(-0.2, 0.4, 0.6)),
)

sensor = scene.add_sensor(
    gs.sensors.SurfaceDistanceProbe(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("palm").idx_local,
        probe_local_pos=((0.0, 0.0, 0.0),),  # one probe at the palm-link origin
        probe_radius=0.5,                     # max sensing range, meters
        track_link_idx=(duck.base_link_idx,),  # global link idx to measure against
    )
)

scene.build()
scene.step()

distances = sensor.read()        # shape ([n_envs,] n_probes), meters
points = sensor.nearest_points   # shape ([n_envs,] n_probes, 3), world frame
```

## Probes and tracked links

A probe is a point fixed in a link's local frame. `probe_local_pos` is a sequence of `(x, y, z)` offsets in meters, one per probe, all mounted on the link named by `link_idx_local` on the entity `entity_idx`. Mounting several probes on fingertips and the palm, as the example does, gives a cheap spatial picture of how the hand is approaching an object.

`track_link_idx` lists the links to measure against, as **global** link indices in solver link space, not link-local indices. Read them off the entities you want to track: `duck.base_link_idx` for a single-link mesh, or `entity.get_link(name).idx` for a specific link of an articulated entity. The sensor queries the triangle faces of every mesh geom on those links, so distances are to actual surfaces, not bounding boxes or centers.

## Reading the sensor

`read()` returns the nearest surface distance for each probe:

```python
distances = sensor.read()  # shape ([n_envs,] n_probes), meters
```

The matching nearest points are a separate attribute rather than part of `read()`:

```python
points = sensor.nearest_points  # shape ([n_envs,] n_probes, 3), world frame
```

Both leading dimensions follow the batched-optional convention: the `[n_envs,]` axis is present only when the scene is built with multiple environments. `nearest_points` is written on each step, so read it after at least one `scene.step()`; before the first step it holds zeros.

## Behavior and units

- **Units.** Distances and probe positions are in meters. The scene uses a right-handed, Z-up frame, and `nearest_points` are in world coordinates.
- **Clamping at `probe_radius`.** `probe_radius` is the maximum sensing range. When no tracked surface lies within it, the reported distance is clamped to `probe_radius` and the nearest point is the probe's own world position. `probe_radius` accepts a scalar shared by every probe, or a per-probe array matching the probe count; it defaults to 0.5 m.
- **Debug drawing.** With `draw_debug=True` and an active visualizer, the sensor draws a small opaque marker sphere at each probe (`debug_probe_center_radius`, default 0.0008 m), a translucent outer sphere sized to `probe_radius` (`debug_probe_sphere_opacity`, default 0.3; set to `0.0` to hide it), and a line to the nearest surface point.

<video preload="auto" controls="True" width="100%" aria-label="Shadow Hand with proximity probes on its palm and fingertips; lines connect each probe to the nearest point on a tracked duck mesh and box as the hand moves">
<source src="../../_static/videos/proximity.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## See also

- {doc}`Sensors overview <index>`: how sensors are sampled, read, and configured with noise, delay, and history.
- {doc}`Raycaster sensors <raycaster>`: distance measurements by casting rays instead of querying nearest surface points.
