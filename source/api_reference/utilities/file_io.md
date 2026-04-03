# File I/O Utilities

Genesis provides utilities for file operations, path handling, and loading robot/scene descriptions.

## Cache Directories

Genesis caches compiled kernels and processed assets:

```python
import genesis as gs

# Get cache directory paths
cache_dir = gs.utils.get_cache_dir()
gsd_cache = gs.utils.get_gsd_cache_dir()

# Get source directory
src_dir = gs.utils.get_src_dir()
```

## URDF Loading

URDF (Unified Robot Description Format) files can be loaded directly:

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# Load from file path
robot = scene.add_entity(gs.morphs.URDF(file="path/to/robot.urdf"))

# Load with custom settings
robot = scene.add_entity(gs.morphs.URDF(
    file="robot.urdf",
    pos=(0, 0, 0),
    quat=(0, 0, 0, 1),
    fixed=True,
))

scene.build()
```

### URDF Customization

```python
# Override link properties
robot = scene.add_entity(gs.morphs.URDF(
    file="robot.urdf",
    links_props={
        "link_name": {
            "mass": 1.0,
            "inertia": [0.1, 0.1, 0.1],
        },
    },
))
```

## MJCF Loading

MuJoCo XML format (MJCF) is also supported:

```python
# Load MJCF model
robot = scene.add_entity(gs.morphs.MJCF(file="model.xml"))

# With customization
robot = scene.add_entity(gs.morphs.MJCF(
    file="model.xml",
    pos=(0, 0, 0.5),
))
```

## Mesh Loading

Genesis supports various mesh formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| OBJ | `.obj` | Wavefront OBJ |
| STL | `.stl` | Stereolithography |
| PLY | `.ply` | Polygon File Format |
| GLB/GLTF | `.glb`, `.gltf` | GL Transmission Format |
| DAE | `.dae` | COLLADA |
| USD | `.usd`, `.usda`, `.usdc` | Universal Scene Description |

```python
# Load mesh entity
mesh = scene.add_entity(gs.morphs.Mesh(
    file="object.obj",
    pos=(0, 0, 0.5),
    scale=0.01,  # Scale factor
))
```

## Asset Paths

Genesis looks for assets in:

1. Absolute path (if provided)
2. Relative to current working directory
3. Genesis assets directory

```python
# Absolute path
robot = scene.add_entity(gs.morphs.URDF(file="/home/user/robot.urdf"))

# Relative path
robot = scene.add_entity(gs.morphs.URDF(file="robots/my_robot.urdf"))

# Genesis built-in assets
plane = scene.add_entity(gs.morphs.Plane())
```

## See Also

- {doc}`/api_reference/options/morph/file_morph/index` - File-based morphs
- {doc}`/api_reference/entity/index` - Entity loading
