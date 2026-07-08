# BatchRenderer

The `BatchRenderer` provides high-throughput parallel rendering optimized for large-scale reinforcement learning training with many parallel environments.

## Overview

The BatchRenderer is designed for:

- **Maximum throughput**: Optimized for rendering thousands of environments
- **Parallel execution**: Native support for batched simulation
- **RL training**: Efficient observation generation for policy learning
- **GPU acceleration**: Full GPU pipeline for minimal CPU overhead

## Quick start

```python
import genesis as gs

gs.init()

# Create scene with multiple environments
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# Add batch renderer camera
cam = scene.add_camera(
    res=(84, 84),
    pos=(2, 0, 1),
    lookat=(0, 0, 0.5),
)

# Build with parallel environments
scene.build(n_envs=1024)

# Training loop
for step in range(10000):
    # Get batched observations
    obs, _, _, _ = cam.render(rgb=True)  # Shape: (n_envs, H, W, 3)

    # Policy inference...
    actions = policy(obs)

    # Step all environments
    scene.step()
```

## Configuration

The BatchRenderer is configured through `gs.options.renderers.BatchRenderer`, which exposes a single parameter:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_rasterizer` | bool | `False` | Whether to use the rasterizer backend instead of ray tracing. |

```python
renderer = gs.options.renderers.BatchRenderer(use_rasterizer=False)
```

## Lighting

The batch renderer manages its own lights, added through `scene.visualizer.add_light` after the scene is created. All arguments are required:

```python
scene.visualizer.add_light(
    pos=(0.0, 0.0, 10.0),      # light position, used for non-directional lights
    dir=(0.0, 0.0, -1.0),      # direction the light travels along (normalized internally)
    color=(1.0, 1.0, 1.0),     # RGB, each channel in [0, 1]
    intensity=1.0,
    directional=True,          # parallel rays if True, positional light if False
    castshadow=True,
    cutoff=45.0,               # spotlight cutoff angle in degrees
    attenuation=0.0,           # falloff with distance for positional lights
)
```

## Output format

With `n_envs > 1`, camera outputs are batched:

| Output | Shape | Description |
|--------|-------|-------------|
| `rgb` | `(n_envs, H, W, 3)` | Batched RGB images |
| `depth` | `(n_envs, H, W)` | Batched depth maps |
| `segmentation` | `(n_envs, H, W)` | Batched segmentation |
| `normal` | `(n_envs, H, W, 3)` | Batched surface normals |

## Performance tips

1. **Resolution**: Use smaller resolutions (64x64 or 84x84) for RL
2. **Render frequency**: Render only when needed, not every step
3. **GPU memory**: Monitor VRAM usage with many environments

## API reference

```{eval-rst}
.. autoclass:: genesis.vis.batch_renderer.BatchRenderer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See also

- {doc}`rasterizer` - Standard rasterization renderer
- {doc}`/api_reference/options/renderer/batchrenderer` - BatchRenderer options
