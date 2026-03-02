# 🎬 Batch Renderer

The BatchRenderer uses Madrona GPU batch rendering for high-throughput multi-environment simulations.

## Installation

```bash
pip install gs-madrona
```

**Requirements:** Linux x86-64, NVIDIA CUDA, Python >= 3.10

## Basic Setup

```python
import genesis as gs

gs.init(backend=gs.cuda)  # CUDA required

scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(use_rasterizer=True),
)

plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# All batch cameras must have identical resolution
cam1 = scene.add_camera(res=(256, 256), pos=(2, 0, 1), lookat=(0, 0, 0.5))
cam2 = scene.add_camera(res=(256, 256), pos=(0, 2, 1), lookat=(0, 0, 0.5))

scene.build(n_envs=128)
```

## Rendering

```python
for step in range(1000):
    scene.step()

    # Render single camera
    rgb, depth, seg, normal = cam1.render(
        rgb=True, depth=True, segmentation=True, normal=True
    )
    # Shape: (n_envs, H, W, C)

    # Or render all cameras at once
    all_rgb = scene.render_all_cameras(rgb=True)
    # Shape: (n_cameras, n_envs, H, W, 3)
```

## Camera Sensor API

```python
camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
        near=0.1,
        far=100.0,
        lights=[{
            "pos": (2.0, 2.0, 5.0),
            "color": (1.0, 1.0, 1.0),
            "intensity": 1.0,
            "directional": True,
            "castshadow": True,
        }],
    )
)

scene.build(n_envs=64)

data = camera.read()  # Returns CameraData with .rgb tensor
```

## Lighting

```python
scene.add_light(
    pos=(0.0, 0.0, 3.0),
    dir=(0.0, 0.0, -1.0),
    color=(1.0, 1.0, 1.0),
    intensity=1.0,
    directional=True,
    castshadow=True,
)
```

## Segmentation

```python
scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(),
    vis_options=gs.options.VisOptions(
        segmentation_level="link",  # "entity", "link", or "geom"
    ),
)

# After rendering
_, _, seg, _ = camera.render(segmentation=True)
colored = scene.visualizer.colorize_seg_idxc_arr(seg)
```

## Performance Tips

- Use identical resolution for all cameras
- Prefer `use_rasterizer=True` for speed
- Batch render all cameras with `scene.render_all_cameras()`
- Typical setup: 256x256 resolution with 128-256 environments
