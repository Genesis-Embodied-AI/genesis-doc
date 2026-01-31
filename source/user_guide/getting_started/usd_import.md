# 📦 Loading USD Scenes

Genesis supports loading complex scenes from Universal Scene Description (USD) files, enabling you to import articulated robots, rigid objects, and complete environments with proper physics properties and joint configurations. USD is an open-source framework developed by Pixar for describing, composing, simulating, and collaborating within 3D worlds.

This tutorial will guide you through loading USD files in Genesis, configuring parsing options, and working with USD-based scenes. The parser is designed to work seamlessly with assets exported from popular tools like NVIDIA Isaac Sim, while also supporting standard USD physics schemas.

## Installation

To load USD assets into Genesis scenes, install the required dependencies:

```bash
pip install -e .[usd]
```

### Optional: USD Material Baking

For advanced material parsing beyond `UsdPreviewSurface`, you can optionally install Omniverse Kit for USD material baking. This feature is only available for Python 3.10 and 3.11 and GPU backend. (For Python 3.12, there is possibility that most of materials in the scene are baked successfully, but some will leave unbaked.)

```bash
pip install --extra-index-url https://pypi.nvidia.com/ omniverse-kit
export OMNI_KIT_ACCEPT_EULA=yes
```

**Note:** The `OMNI_KIT_ACCEPT_EULA` environment variable must be set to accept the EULA. This is a one-time operation. Once set, it will not prompt again. If USD baking is disabled, Genesis will only parse materials of type `UsdPreviewSurface`.

If you encounter the Genesis warning "Baking process failed: ...", here are some troubleshooting tips:

- **EULA Acceptance**: The first launch may require accepting the Omniverse EULA. Accept it in runtime or set `OMNI_KIT_ACCEPT_EULA=yes` to accept it automatically.

- **IOMMU Warning**: A window showing "IOMMU Enabled" warning may pop up on the first launch. Click "OK" promptly to avoid timeout.

- **Initial Installation**: The first launch may install additional dependencies, which can cause a timeout. Run your program again after installation completes; subsequent runs will not require installation.

- **Multiple Python Environments**: If you have multiple Python environments (especially with different Python versions), Omniverse Kit extensions may conflict across environments. Remove the shared Omniverse extension folder (e.g., `~/.local/share/ov/data/ext` on Linux) and try again.

## Overview

Genesis's USD parser supports the following features:

### Joint Types

- **Revolute Joints** (`UsdPhysics.RevoluteJoint`): Rotational joints with angular limits
- **Prismatic Joints** (`UsdPhysics.PrismaticJoint`): Linear/sliding joints with distance limits
- **Spherical Joints** (`UsdPhysics.SphericalJoint`): Ball joints with 3 rotational degrees of freedom
- **Fixed Joints** (`UsdPhysics.FixedJoint`): Rigid connections between links
- **Free Joints** (`UsdPhysics.Joint` with type "PhysicsJoint"): 6-DOF joints with full translational and rotational freedom

### Physics Properties

- **Joint limits** (lower/upper bounds): Supported for revolute and prismatic joints
- **Joint friction** (`dofs_frictionloss`): Supported for revolute, prismatic, and spherical joints
- **Joint armature** (`dofs_armature`): Supported for revolute, prismatic, and spherical joints
- **Joint stiffness** (`dofs_stiffness`): Passive property supported for revolute and prismatic joints
- **Joint damping** (`dofs_damping`): Passive property supported for revolute and prismatic joints
- **Drive API** (`dofs_kp`, `dofs_kv`, `dofs_force_range`): PD control parameters supported for revolute, prismatic, and spherical joints

### Geometry

- **Visual geometries**: Parsed from USD geometry prims matching visual patterns
- **Collision geometries**: Parsed from USD geometry prims matching collision patterns

### Materials and Rendering

- **UsdPreviewSurface**: Fully supported with diffuse color, opacity, metallic, roughness, emissive, normal maps, and IOR
- **Material baking**: Optional support via Omniverse Kit for complex materials beyond **UsdPreviewSurface**
- **Display colors**: Fallback to `displayColor` when materials are not available

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

USD files can contain multiple rigid entities (articulations and rigid bodies) in a single file. Genesis provides two methods for loading USD:

- **`scene.add_stage()`**: Automatically discovers and loads **all** rigid entities in the USD file. This is the recommended method for loading complete USD scenes with multiple entities.

- **`scene.add_entity()`**: Loads a **single** entity from the USD file. If `prim_path` is not specified, it uses the USD stage's default prim. Set `prim_path` to target a specific prim in the stage.

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

Genesis can parse collision and visual geometries from USD files. You can configure regex patterns to identify which prims should be treated as collision-only or visual-only geometry. The parser uses `re.match()` to check if a prim's name matches each pattern from the start of the string.

**Recognition Rules:**

1. **Pattern Matching**: The parser recursively traverses the prim hierarchy. For each prim, it checks the prim's name against the patterns in order. Once a prim matches a pattern, it is marked as visual-matched or collision-matched, and this classification is inherited by all its child prims recursively.

2. **Geometry Classification**: 
   - A prim matching a visual pattern is treated as visual-only geometry (not used for collision detection).
   - A prim matching a collision pattern is treated as collision-only geometry (not used for visualization).
   - A prim matching both patterns is treated as both visual and collision geometry.
   - A prim matching neither pattern is also treated as both visual and collision geometry (this is the default behavior for mesh-only USD assets).

3. **Visibility and Purpose**: Only visible prims (not marked as "invisible") are parsed. Prims with purpose "guide" are excluded from visual geometry but can still be collision geometry.

**Example Configuration:**

```python
gs.morphs.USD(
    file="robot.usd",
    # Regex patterns to identify collision meshes (tried in order)
    collision_mesh_prim_patterns=[
        r"^([cC]ollision).*",  # Matches prims starting with "Collision" or "collision"
    ],
    # Regex patterns to identify visual meshes
    visual_mesh_prim_patterns=[
        r"^([vV]isual).*",     # Matches prims starting with "Visual" or "visual"
    ],
)
```

**Example Stage Structures:**

- **Direct geometry on rigid body**: The geometry prim itself doesn't match any pattern, so it's treated as both visual and collision.

    ```usd
    def Cube "Cube" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
    }
    ```
- **Separate visual and collision children**: Direct children matching patterns are treated accordingly, and the match propagates to their subtrees.

    ```usd
    def Xform "ObjectA" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Cube "Visual"      # Matches visual pattern → visual-only
            {
            }

            def Cube "Collision"   # Matches collision pattern → collision-only
            {
            }
        }
    ```
- **Nested hierarchies**: Once a parent matches a pattern, all descendants inherit that classification.

    ```usd
    def Xform "ObjectB" (
            prepend apiSchemas = ["PhysicsRigidBodyAPI"]
        )
        {
            def Xform "Visual"     # Matches visual pattern
            {
                def Mesh "Cube"    # Inherits visual-only (entire subtree)
                {
                }
                def Mesh "Sphere"  # Inherits visual-only
                {
                }
            }

            def Xform "Collision" # Matches collision pattern
            {
                def Cube "Cube"   # Inherits collision-only (entire subtree)
                {
                }
            }
        }
    ```
- **No pattern match**: Prims that don't match any pattern are treated as both visual and collision.
    ```usd
    def Xform "ObjectC" (
        prepend apiSchemas = ["PhysicsRigidBodyAPI"]
    )
    {
        def Mesh "Whatever"  # No pattern match → both visual and collision
        {
        }
    }
    ```


## Next Steps

- Learn about [controlling robots](control_your_robot.md) in Genesis
- Explore [inverse kinematics](inverse_kinematics_motion_planning.md) for USD-loaded robots
- Check out [parallel simulation](parallel_simulation.md) for training with USD assets
- See the [API reference](../../api_reference/options/morph/file_morph/file_morph.md) for detailed USD morph options
- See the [conventions](conventions.md) for more details on the coordinate system and mathematical conventions used throughout Genesis.
