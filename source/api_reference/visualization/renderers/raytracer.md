# Raytracer

The `Raytracer` provides photorealistic rendering using path tracing. It's designed for generating high-quality images and videos.

## Overview

The Raytracer offers:

- **Photorealistic quality**: Global illumination, reflections, refractions
- **Physical accuracy**: Correct light transport simulation
- **Advanced materials**: PBR materials, subsurface scattering
- **Denoising**: AI-based denoising for faster convergence

## Quick Start

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# Add entities with materials
plane = scene.add_entity(
    gs.morphs.Plane(),
    surface=gs.surfaces.Plastic(),
)
box = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5)),
    surface=gs.surfaces.Metal.Gold(),
)

scene.build()

# Add raytracer camera
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
    spp=256,        # Samples per pixel
    denoise=True,   # Enable denoising
)

# Render high-quality image
scene.step()
rgb = cam.render(rgb=True)
```

## Configuration

Key parameters for raytracer cameras:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `spp` | Samples per pixel (higher = less noise) | 256 |
| `denoise` | Enable AI denoising | False |
| `model` | Camera model (`pinhole` or `thinlens`) | `pinhole` |
| `aperture` | Aperture for depth of field | 0.0 |
| `focus_dist` | Focus distance | Auto |

## Thin Lens (Depth of Field)

```python
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="thinlens",
    aperture=0.1,      # Larger = more blur
    focus_dist=3.0,    # Distance to focus plane
    spp=512,
)
```

## Materials for Raytracing

The raytracer supports advanced surface materials:

- **Plastic**: Diffuse with optional roughness
- **Metal**: Reflective metallic surfaces (Gold, Copper, Iron, etc.)
- **Glass**: Transparent/refractive materials
- **Emission**: Light-emitting surfaces

See {doc}`/api_reference/options/surface/index` for all surface types.

## API Reference

```{eval-rst}
.. autoclass:: genesis.vis.raytracer.Raytracer
   :members:
   :undoc-members:
   :show-inheritance:
```

## See Also

- {doc}`rasterizer` - Fast rasterization renderer
- {doc}`/api_reference/options/surface/index` - Surface materials
- {doc}`/api_reference/options/renderer/raytracer` - Raytracer options
