# 📦 Loading USD Scenes

Genesis supports loading complex scenes from Universal Scene Description (USD) files, enabling you to import articulated robots, rigid objects, and complete environments with proper physics properties and joint configurations. USD is an open-source framework developed by Pixar for describing, composing, simulating, and collaborating within 3D worlds.

This tutorial will guide you through loading USD files in Genesis, configuring parsing options, and working with USD-based scenes. The parser is designed to work seamlessly with assets exported from popular tools like NVIDIA Isaac Sim, while also supporting standard USD physics schemas.

## Overview

Genesis's USD parser supports the following features:

### Joint Types

- **Revolute Joints**: Rotational joints with angular limits
- **Prismatic Joints**: Linear/sliding joints with distance limits
- **Spherical Joints**: Ball joints with 3 rotational degrees of freedom
- **Fixed Joints**: Rigid connections between links

### Physics Properties

- Joint limits (lower/upper bounds)
- Joint friction
- Joint armature (rotor inertia)
- Joint stiffness and damping
- Drive API (for PD control parameters)

### Geometry

- Visual meshes
- Collision meshes

## Basic Example

Let's start with a simple example that loads a USD file containing an articulated object:

```python
import genesis as gs
from huggingface_hub import snapshot_download

# Initialize Genesis
gs.init(backend=gs.cpu)

# Create a scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    show_viewer=True,
)

# Download a USD asset (example from Genesis assets)
asset_path = snapshot_download(
    repo_type="dataset",
    repo_id="Genesis-Intelligence/assets",
    revision="c50bfe3e354e105b221ef4eb9a79504650709dd2",
    allow_patterns="usd/Refrigerator055/*",
    max_workers=1,
)

# Load the USD stage
entities = scene.add_stage(
    morph=gs.morphs.USD(
        file=f"{asset_path}/usd/Refrigerator055/Refrigerator055.usd",
    ),
)

# Build and simulate
scene.build()
```

The key difference from loading other formats is using `scene.add_stage()` instead of `scene.add_entity()`. The `add_stage()` method is designed for formats that can contain multiple entities in a single file, allowing it to handle complex scene hierarchies with multiple entities.

## USD Morph Configuration

The `gs.morphs.USD` class provides extensive configuration options for controlling how USD files are parsed:

### Joint Dynamics Configuration

Genesis can parse joint properties from USD attributes. 

Because some joint physics properties are not part of the USD standard, Genesis provides default attribute name candidates that accommodate well-established exporters, notably Isaac Sim, which uses custom attributes like `physxJoint:jointFriction` and `physxLimit:angular:stiffness`.

For example, the following code configures the attribute name candidates for joint friction. The parser will try these candidates in order and use the first one that is found.

```python
gs.morphs.USD(
    file="robot.usd",
    # Joint friction attributes (tried in order)
    joint_friction_attr_candidates=[
        "physxJoint:jointFriction",  # Isaac Sim compatibility
        "physics:jointFriction",
        "jointFriction",
        "friction",
    ],
)
```

Supported attributes are listed in the following table:

| Genesis Attribute Name | Source / Default Attribute Name Candidates | Description |
|----------------|-------------|-------------|
| `dofs_frictionloss` | `["physxJoint:jointFriction", "physics:jointFriction", "jointFriction", "friction"]` | Joint friction (passive property) |
| `dofs_armature` | `["physxJoint:armature", "physics:armature", "armature"]` | Joint armature (passive property) |
| `dofs_kp` | `"physics:stiffness"` | PD control proportional gain (kp) - from DriveAPI |
| `dofs_kv` | `"physics:angular:damping"` | PD control derivative gain (kv) - from DriveAPI |
| `dofs_stiffness` | **Revolute joints:** `["physxLimit:angular:stiffness", "physics:stiffness", "stiffness"]`<br>**Prismatic joints:** `["physxLimit:linear:stiffness", "physxLimit:X:stiffness", "physxLimit:Y:stiffness", "physxLimit:Z:stiffness", "physics:linear:stiffness", "linear:stiffness"]` | Passive joint stiffness (depends on joint type) |
| `dofs_damping` | **Revolute joints:** `["physxLimit:angular:damping", "physics:angular:damping", "angular:damping"]`<br>**Prismatic joints:** `["physxLimit:linear:damping", "physxLimit:X:damping", "physxLimit:Y:damping", "physxLimit:Z:damping", "physics:linear:damping", "linear:damping"]` | Passive joint damping (depends on joint type) |

Note that, attribute name within bracket (`[...]`) is unofficial USD attribute, user can setup their own attribute name candidates to customize the parsing behavior, while the attribute name without bracket (`...`) is official USD attribute, which is parsed from the USD file directly.

### Geometry Parsing Options

Genesis can parse collision and visual meshes from USD files. You can configure which regex patterns to use to identify the collision and visual meshes, which are tried in order. In most cases, the default patterns are enough.

The recognition rules are:

- If a rigid body prim itself is a [UsdGeom](https://openusd.org/release/api/usd_geom_page_front.html), it's regarded as both collision and visual mesh.
- If any direct child prim of a rigid body prim matches the collision mesh pattern, its subtree will be regarded as collision meshes of the rigid body.
- If any direct child prim of a rigid body prim matches the visual mesh pattern, its subtree will be regarded as visual meshes of the rigid body.

For example, the following code configures the regex patterns to identify the collision and visual meshes. The parser will try these patterns in order and use the first one that is found. Users can also provide their own regex patterns to customize the parsing behavior.

```python
gs.morphs.USD(
    file="robot.usd",
    # Regex patterns to identify collision meshes (tried in order)
    collision_mesh_prim_patterns=[
        r"^([cC]ollision).*",  # Matches UsdGeom starting with "Collision" or "collision"
        r"^.*",                # Fallback: match all UsdGeom prims
    ],
    # Regex patterns to identify visual meshes
    visual_mesh_prim_patterns=[
        r"^([vV]isual).*",     # Matches UsdGeom starting with "Visual" or "visual"
        r"^.*",                # Fallback: match all UsdGeom prims
    ],
)
```

The following are some examples of stage tree structures that can be correctly recognized by the parser:

- `Cube` is a UsdGeom with rigid body API itself, so it is regarded as both collision and visual mesh.

    ```usd
    def Cube "Cube" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
    }
    ```
- `ObjectA` is an Xform with two children `Visual` and `Collision`, both of which are UsdGeom prims, so the children are regarded as collision and visual meshes of the parent.

    ```usd
    def Xform "ObjectA" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Cube "Visual"
            {
            }

            def Cube "Collision"
            {
            }
        }
    ```
- `ObjectB` is an Xform with children `Visual` and `Collision`, which are Xforms with two children `Cube` and `Sphere`, so the children (and their subtrees) are regarded as visual and collision meshes of `ObjectB`.

    ```usd
    def Xform "ObjectB" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Xform "Visual"
            {
                def Mesh "Cube"
                {
                }
                def Mesh "Sphere"
                {
                }
            }

            def Xform "Collision"
            {
                def Cube "Cube"
                {
                }
                def Sphere "Sphere"
                {

                }
            }
        }
    ```
- `ObjectC` is an Xform with a child `Whatever`, matching the fallback pattern `^.*`, so the child is regarded as both collision and visual mesh of the parent.
    ```usd
    def Xform "ObjectC" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
        def Mesh "Whatever"
        {
        }
    }
    ```



## Limitations and Notes

1. **Unit System**: Arbitrary unit systems are not supported. Genesis only supports SI units (meters and kilograms).

2. **Scaling**: Programmatic scaling factors are not supported. The scale is always assumed to be 1.0, but users can manually edit the scene root transform if needed.

3. **Rendering Properties**: Rendering properties such as materials, textures, etc. are not currently supported.

## Next Steps

- Learn about [controlling robots](control_your_robot.md) in Genesis
- Explore [inverse kinematics](inverse_kinematics_motion_planning.md) for USD-loaded robots
- Check out [parallel simulation](parallel_simulation.md) for training with USD assets
- See the [API reference](../../api_reference/options/morph/file_morph/file_morph.md) for detailed USD morph options
- See the [conventions](../conventions.md) for more details on the coordinate system and mathematical conventions used throughout Genesis.
