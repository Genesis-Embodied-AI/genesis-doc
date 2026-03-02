# BatchRenderer

The `BatchRenderer` provides high-throughput parallel rendering optimized for large-scale reinforcement learning training with many parallel environments.

## Overview

The BatchRenderer is designed for:

- **Maximum throughput**: Optimized for rendering thousands of environments
- **Parallel execution**: Native support for batched simulation
- **RL training**: Efficient observation generation for policy learning
- **GPU acceleration**: Full GPU pipeline for minimal CPU overhead

## Quick Start

```python
import genesis as gs

gs.init()

# Create scene with multiple environments
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# Build with parallel environments
scene.build(n_envs=1024)

# Add batch renderer camera
cam = scene.add_camera(
    res=(84, 84),
    pos=(2, 0, 1),
    lookat=(0, 0, 0.5),
)

# Training loop
for step in range(10000):
    # Get batched observations
    obs = cam.render(rgb=True)  # Shape: (n_envs, H, W, 3)

    # Policy inference...
    actions = policy(obs)

    # Step all environments
    scene.step()
```

## Configuration

The BatchRenderer is configured through `BatchRendererOptions`:

```python
batch_options = gs.options.BatchRendererOptions(
    # Configuration options
)
```

## Output Format

With `n_envs > 1`, camera outputs are batched:

| Output | Shape | Description |
|--------|-------|-------------|
| `rgb` | `(n_envs, H, W, 3)` | Batched RGB images |
| `depth` | `(n_envs, H, W)` | Batched depth maps |
| `segmentation` | `(n_envs, H, W)` | Batched segmentation |

## Performance Tips

1. **Resolution**: Use smaller resolutions (64x64 or 84x84) for RL
2. **Render frequency**: Render only when needed, not every step
3. **GPU memory**: Monitor VRAM usage with many environments

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.batch_renderer.BatchRenderer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`rasterizer` - Standard rasterization renderer
- {doc}`/api_reference/options/renderer/batchrenderer` - BatchRenderer options
