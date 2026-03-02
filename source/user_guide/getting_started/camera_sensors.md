# 📷 Camera Sensors

Genesis provides three camera sensor backends for rendering RGB images in simulations.

## Camera Sensor Types

| Sensor | Backend | Multi-Env | Best For |
|--------|---------|-----------|----------|
| `RasterizerCameraSensor` | OpenGL | Sequential | Fast real-time rendering |
| `RaytracerCameraSensor` | LuisaRender | Single only | Photo-realistic images |
| `BatchRendererCameraSensor` | Madrona GPU | Parallel | High-throughput RL training |

## Basic Usage

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(morph=gs.morphs.Plane())

# Add a camera sensor
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

# Read rendered image
data = camera.read()
print(data.rgb.shape)  # (512, 512, 3) for single env
```

## Camera Options

### Common Parameters (All Backends)

```python
gs.sensors.RasterizerCameraOptions(
    res=(512, 512),              # (width, height)
    pos=(3.0, 0.0, 2.0),         # Position (world or local if attached)
    lookat=(0.0, 0.0, 0.0),      # Look-at point
    up=(0.0, 0.0, 1.0),          # Up vector
    fov=60.0,                    # Vertical FOV in degrees
    entity_idx=-1,               # Entity to attach to (-1 = static)
    link_idx_local=0,            # Link index for attachment
)
```

### Raytracer-Specific

```python
gs.sensors.RaytracerCameraOptions(
    model="pinhole",             # "pinhole" or "thinlens"
    spp=256,                     # Samples per pixel
    denoise=False,               # Apply denoising
    aperture=2.8,                # Depth-of-field (thinlens)
    focus_dist=3.0,              # Focus distance (thinlens)
)
```

### BatchRenderer-Specific

```python
gs.sensors.BatchRendererCameraOptions(
    near=0.01,                   # Near clip plane
    far=100.0,                   # Far clip plane
    use_rasterizer=True,         # GPU rasterizer mode
)
```

**Note:** All BatchRenderer cameras must have identical resolution.

## Attaching Cameras to Entities

Mount a camera on a robot's end-effector:

```python
robot = scene.add_entity(morph=gs.morphs.URDF(file="robot.urdf"))

camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(640, 480),
        pos=(0.1, 0.0, 0.05),    # Offset from link frame
        lookat=(0.2, 0.0, 0.0),  # Look direction
        entity_idx=robot.idx,    # Attach to robot
        link_idx_local=8,        # End-effector link
    )
)
```

The camera automatically follows the entity's motion.

## Multi-Environment Rendering

```python
scene.build(n_envs=4)

# Set different states per environment
sphere.set_pos([[0, 0, 1], [0.2, 0, 1], [0.4, 0, 1], [0.6, 0, 1]])
scene.step()

# Read all environments
data = camera.read()
print(data.rgb.shape)  # (4, H, W, 3)

# Read specific environments
data = camera.read(envs_idx=[0, 2])
print(data.rgb.shape)  # (2, H, W, 3)
```

## Choosing a Backend

- **Rasterizer**: Default choice, fast, works on all platforms
- **Raytracer**: Use when photo-realism is needed (requires `renderer=gs.renderers.RayTracer()`)
- **BatchRenderer**: Use for RL training with many environments (CUDA only)

```python
# For raytracer, configure scene renderer
scene = gs.Scene(renderer=gs.renderers.RayTracer())

# For batch renderer
scene = gs.Scene(renderer=gs.renderers.BatchRenderer())
```
