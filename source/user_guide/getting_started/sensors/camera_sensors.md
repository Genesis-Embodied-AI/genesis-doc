# 🎥 Camera Sensors

Genesis ships three camera sensor backends for rendering RGB images:

| Sensor | Backend | Multi-Env | Best for |
|---|---|---|---|
| `RasterizerCameraSensor` | OpenGL | Sequential | Fast real-time rendering on any platform |
| `RaytracerCameraSensor` | LuisaRender | Single only | Photo-realistic offline renders |
| `BatchRendererCameraSensor` | Madrona GPU | Parallel | High-throughput RL training (CUDA only) |

## Basic usage

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(morph=gs.morphs.Plane())

camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
    )
)

scene.build(n_envs=1)
scene.step()

data = camera.read()
print(data.rgb.shape)  # (512, 512, 3) for single env
```

## Camera options

### Common parameters (all backends)

```python
gs.sensors.RasterizerCameraOptions(
    res=(512, 512),            # (width, height)
    pos=(3.0, 0.0, 2.0),       # position (world, or local if attached)
    lookat=(0.0, 0.0, 0.0),    # look-at point
    up=(0.0, 0.0, 1.0),        # up vector
    fov=60.0,                  # vertical FOV in degrees
    entity_idx=-1,             # entity to attach to (-1 = static)
    link_idx_local=0,          # link index for attachment
)
```

### Raytracer-specific

```python
gs.sensors.RaytracerCameraOptions(
    model="pinhole",   # "pinhole" or "thinlens"
    spp=256,           # samples per pixel
    denoise=False,     # apply denoising
    aperture=2.8,      # depth-of-field (thinlens)
    focus_dist=3.0,    # focus distance (thinlens)
)
```

### Batch renderer-specific

```python
gs.sensors.BatchRendererCameraOptions(
    near=0.01,
    far=100.0,
    use_rasterizer=True,
)
```

All `BatchRendererCameraSensor` cameras must have identical resolution.

## Attaching cameras to entities

Mount a camera on a robot's end-effector:

```python
robot = scene.add_entity(morph=gs.morphs.URDF(file="robot.urdf"))

camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(640, 480),
        pos=(0.1, 0.0, 0.05),    # offset from link frame
        lookat=(0.2, 0.0, 0.0),  # look direction
        entity_idx=robot.idx,
        link_idx_local=8,        # end-effector link
    )
)
```

The camera automatically follows the entity's motion.

## Multi-environment rendering

```python
scene.build(n_envs=4)

# Set different states per environment
sphere.set_pos([[0, 0, 1], [0.2, 0, 1], [0.4, 0, 1], [0.6, 0, 1]])
scene.step()

data = camera.read()
print(data.rgb.shape)  # (4, H, W, 3)

# Read specific environments
data = camera.read(envs_idx=[0, 2])
print(data.rgb.shape)  # (2, H, W, 3)
```

## Choosing a backend

- **Rasterizer** - default; fast; works on every platform.
- **Raytracer** - use when photo-realism is needed (requires `renderer=gs.renderers.RayTracer()`).
- **BatchRenderer** - use for RL training with many environments (CUDA only).

```python
# For raytracer, configure scene renderer
scene = gs.Scene(renderer=gs.renderers.RayTracer())

# For batch renderer
scene = gs.Scene(renderer=gs.renderers.BatchRenderer())
```

## Batch rendering with Madrona

The Madrona-based batch renderer is the high-throughput option for RL training. It renders many environments and cameras in parallel on GPU.

```bash
pip install gs-madrona
```

**Requirements:** Linux x86-64, NVIDIA CUDA, Python ≥ 3.10.

```python
import genesis as gs

gs.init(backend=gs.cuda)  # CUDA required

scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(use_rasterizer=True),
)

plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

cam1 = scene.add_camera(res=(256, 256), pos=(2, 0, 1), lookat=(0, 0, 0.5))
cam2 = scene.add_camera(res=(256, 256), pos=(0, 2, 1), lookat=(0, 0, 0.5))

scene.build(n_envs=128)
```

### Rendering

```python
for step in range(1000):
    scene.step()

    # Render a single camera with channel selection
    rgb, depth, seg, normal = cam1.render(
        rgb=True, depth=True, segmentation=True, normal=True,
    )
    # Shape: (n_envs, H, W, C)

    # Or render all cameras at once
    all_rgb = scene.render_all_cameras(rgb=True)
    # Shape: (n_cameras, n_envs, H, W, 3)
```

### Camera sensor API

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

data = camera.read()  # CameraData(rgb=...)
```

### Lighting

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

### Segmentation

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

### Performance tips

- Use identical resolution for all cameras.
- Prefer `use_rasterizer=True` for speed.
- Batch render all cameras with `scene.render_all_cameras()`.
- Typical setup: 256×256 resolution with 128–256 environments.
