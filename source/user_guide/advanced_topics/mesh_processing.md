# 🔺 Mesh Processing

Genesis provides mesh utilities for loading, simplification, convex decomposition, and collision processing.

## Loading Meshes

```python
import genesis as gs

# Load from file
entity = scene.add_entity(gs.morphs.Mesh(file="model.obj"))

# With processing options
entity = scene.add_entity(
    gs.morphs.Mesh(
        file="model.obj",
        scale=0.1,
        convexify=True,
        decimate=True,
        decimate_face_num=500,
    )
)
```

## Decimation

Reduce mesh complexity for collision performance:

```python
gs.morphs.Mesh(
    file="high_poly.obj",
    decimate=True,
    decimate_face_num=500,         # Target face count
    decimate_aggressiveness=2,     # 0-8 scale
)
```

**Aggressiveness levels:**
- 0: Lossless
- 2: Preserve features (default)
- 5: Significant reduction
- 8: Maximum reduction

## Convex Decomposition

For collision detection, meshes are decomposed into convex parts:

```python
gs.morphs.Mesh(
    file="concave.obj",
    convexify=True,  # Auto-decompose if needed
)
```

Genesis uses COACD library with configurable options:

```python
gs.options.COACDOptions(
    threshold=0.05,
    max_convex_hull=16,
    resolution=2000,
    preprocess_mode="auto",
)
```

## Collision Processing

Genesis automatically processes collision meshes:

1. **Repair**: Removes duplicate faces
2. **Convexification check**: Tests if simple convex hull is sufficient
3. **Decomposition**: Splits concave meshes into convex parts
4. **Decimation**: Reduces high-poly meshes (>5000 faces warning)

## Tetrahedralization

For FEM/deformable simulation:

```python
entity = scene.add_entity(
    morph=gs.morphs.Mesh(file="model.obj"),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4),
)
# Mesh auto-tetrahedralized for FEM
```

## Mesh Properties

```python
mesh = entity.morph.mesh

verts = mesh.verts      # (N, 3) vertices
faces = mesh.faces      # (M, 3) face indices
normals = mesh.normals  # (N, 3) per-vertex normals
uvs = mesh.uvs          # (N, 2) texture coords

is_convex = mesh.is_convex
volume = mesh.volume
area = mesh.area
```

## Particle Sampling

Sample particles from mesh volume:

```python
mesh.particlize(p_size=0.01, sampler="random")
```

**Samplers:**
- `"random"`: Random sampling
- `"pbs_poisson"`: Poisson disk sampling
- `"pbs_grid"`: Grid-based sampling

## Primitive Meshes

Genesis provides built-in primitives:

```python
gs.morphs.Sphere(radius=0.5)
gs.morphs.Box(size=(1.0, 1.0, 1.0))
gs.morphs.Cylinder(radius=0.3, height=1.0)
gs.morphs.Plane()
```

## Caching

Genesis caches processed meshes for faster loading:

| Cache Type | Extension | Purpose |
|------------|-----------|---------|
| Convex | `.cvx` | Convex decomposition |
| Tetrahedral | `.tet` | FEM tetrahedralization |
| SDF | `.gsd` | Signed distance fields |
| Remesh | `.rm` | Remeshed versions |
| Particles | `.ptc` | Particle sampling |

Cache uses SHA256 hash of input parameters for invalidation.

## Dependencies

- **trimesh**: Core mesh operations
- **fast_simplification**: Decimation
- **coacd**: Convex decomposition
- **pyvista + tetgen**: Tetrahedralization
