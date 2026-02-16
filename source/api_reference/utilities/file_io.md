# File I/O Utilities

Genesis 提供文件操作、路径处理以及加载机器人/场景描述的工具。

## 缓存目录

Genesis 缓存编译后的内核和处理后的资源：

```python
import genesis as gs

# Get cache directory paths
cache_dir = gs.utils.get_cache_dir()
gsd_cache = gs.utils.get_gsd_cache_dir()

# Get source directory
src_dir = gs.utils.get_src_dir()
```

## URDF 加载

可以直接加载 URDF（Unified Robot Description Format）文件：

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

### URDF 自定义

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

## MJCF 加载

也支持 MuJoCo XML 格式（MJCF）：

```python
# Load MJCF model
robot = scene.add_entity(gs.morphs.MJCF(file="model.xml"))

# With customization
robot = scene.add_entity(gs.morphs.MJCF(
    file="model.xml",
    pos=(0, 0, 0.5),
))
```

## Mesh 加载

Genesis 支持多种 mesh 格式：

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

## 资源路径

Genesis 在以下位置查找资源：

1. 绝对路径（如果提供）
2. 相对于当前工作目录
3. Genesis 资源目录

```python
# Absolute path
robot = scene.add_entity(gs.morphs.URDF(file="/home/user/robot.urdf"))

# Relative path
robot = scene.add_entity(gs.morphs.URDF(file="robots/my_robot.urdf"))

# Genesis built-in assets
plane = scene.add_entity(gs.morphs.Plane())
```

## 另请参阅

- {doc}`/api_reference/options/morph/file_morph/index` - 基于文件的 morphs
- {doc}`/api_reference/entity/index` - 实体加载
