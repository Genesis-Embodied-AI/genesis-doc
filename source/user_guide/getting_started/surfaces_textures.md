# 🎨 Surfaces and Textures

Genesis provides material and texture configuration for rendering.

## Surface Types

| Surface | Description |
|---------|-------------|
| `Rough` | Matte, non-reflective (roughness=1.0) |
| `Smooth` | Polished plastic (roughness=0.1) |
| `Reflective` | Highly reflective (roughness=0.01) |
| `Glass` | Transparent with refraction |
| `Metal` | Metallic surfaces (Iron, Gold, etc.) |
| `Water` | Water-like surface |
| `Emission` | Light-emitting surface |

## Basic Usage

```python
import genesis as gs

scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0, 0, 1), radius=0.5),
    surface=gs.surfaces.Smooth(color=(0.8, 0.2, 0.2)),
)
```

## Surface Properties

```python
gs.surfaces.Smooth(
    color=(1.0, 1.0, 1.0),    # RGB (0-1)
    roughness=0.1,            # 0=mirror, 1=matte
    metallic=0.0,             # 0=dielectric, 1=metal
    opacity=1.0,              # Transparency
    emissive=(0.0, 0.0, 0.0), # Self-illumination
    ior=1.5,                  # Index of refraction
)
```

## Metallic Surfaces

```python
# Predefined metals
gs.surfaces.Iron()
gs.surfaces.Gold()
gs.surfaces.Copper()
gs.surfaces.Aluminium()

# Custom metal
gs.surfaces.Metal(metal_type="gold", roughness=0.15)
```

## Transparent Surfaces

```python
# Glass
gs.surfaces.Glass(
    color=(0.9, 0.9, 1.0, 0.7),  # RGBA
    roughness=0.1,
    ior=1.5,
)

# Water
gs.surfaces.Water()
```

## Textures

### Color Texture

```python
gs.textures.ColorTexture(color=(1.0, 0.0, 0.0))
```

### Image Texture

```python
gs.textures.ImageTexture(
    image_path="textures/checker.png",
    encoding="srgb",  # or "linear" for non-color data
)
```

### Using Textures with Surfaces

```python
surface = gs.surfaces.Rough(
    diffuse_texture=gs.textures.ImageTexture(image_path="albedo.png"),
    roughness_texture=gs.textures.ImageTexture(image_path="roughness.png", encoding="linear"),
    normal_texture=gs.textures.ImageTexture(image_path="normal.png", encoding="linear"),
)
```

## Visualization Modes

```python
# Particle visualization (for fluids)
gs.surfaces.Rough(color=(0.6, 0.8, 1.0), vis_mode="particle")

# Surface reconstruction
gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7), vis_mode="recon")
```

## Environment Maps (Raytracer)

```python
scene = gs.Scene(
    renderer=gs.renderers.RayTracer(
        env_surface=gs.surfaces.Emission(
            emissive_texture=gs.textures.ImageTexture(image_path="hdri.hdr")
        ),
        env_radius=15.0,
    )
)
```
