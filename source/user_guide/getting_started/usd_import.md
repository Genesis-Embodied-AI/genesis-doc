# 📦 Loading USD Scenes

Genesis supports loading complex scenes from Universal Scene Description (USD) files, enabling you to import articulated robots, rigid objects, and complete environments with proper physics properties, materials, and joint configurations. USD is an open-source framework developed by Pixar for describing, composing, simulating, and collaborating within 3D worlds.

This tutorial will guide you through loading USD files in Genesis, configuring parsing options, and working with USD-based scenes.

## Overview

USD support in Genesis allows you to:

- Load complete articulated robots with joints, limits, and dynamics
- Import rigid objects with proper collision and visual meshes
- Support Isaac Sim and other USD-compatible asset formats

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
    rigid_options=gs.options.RigidOptions(
        dt=0.002,
        gravity=(0, 0, -9.8),
        enable_collision=True,
        enable_joint_limit=True,
        max_collision_pairs=1000,
    ),
    show_viewer=True,
)

# Download a USD asset (example from Genesis assets)
asset_path = snapshot_download(
    repo_type="dataset",
    repo_id="Genesis-Intelligence/assets",
    revision="main",
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

for i in range(1000):
    scene.step()
```

The key difference from loading other formats is using `scene.add_stage()` instead of `scene.add_entity()`. The `add_stage()` method is specifically designed for USD files and can handle complex scene hierarchies with multiple entities.

## USD Morph Configuration

The `gs.morphs.USD` class provides extensive configuration options for controlling how USD files are parsed:

### Joint Dynamics Configuration

Genesis can parse joint properties from USD attributes. You can configure which attribute names to look for. In most cases, the default attribute name candidates should be enough.

For example, the following code configures the attribute name candidates for joint friction . The parser will try these names in order and use the first one that is found. Users can also provide their own attribute name candidates to customize the parsing behavior.

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

| Genesis Attribute Name | Default Attribute Name Candidates | Description |
|----------------|-------------|-------------|
| `dofs_frictionloss` | `["physxJoint:jointFriction", "physics:jointFriction", "jointFriction", "friction"]` | Joint friction |
| `dofs_armature` | `["physxJoint:armature", "physics:armature", "armature"]` | Joint armature |
| `dofs_kp` | `["physxLimit:angular:stiffness", "physics:stiffness", "stiffness"]` | Joint stiffness |
| `dofs_kv` | `["physxLimit:angular:damping", "physics:angular:damping", "angular:damping"]` | Joint damping |
| `dofs_stiffness` | `["physxLimit:linear:stiffness", "physxLimit:X:stiffness", "physxLimit:Y:stiffness", "physxLimit:Z:stiffness", "physics:linear:stiffness", "linear:stiffness"]` | Joint stiffness |
| `dofs_damping` | `["physxLimit:linear:damping", "physxLimit:X:damping", "physxLimit:Y:damping", "physxLimit:Z:damping", "physics:linear:damping", "linear:damping"]` | Joint damping |

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
        r"^([cC]ollision).*",  # Matches prims starting with "Collision" or "collision"
        r"^.*",                # Fallback: match all prims
    ],
    # Regex patterns to identify visual meshes
    visual_mesh_prim_patterns=[
        r"^([vV]isual).*",     # Matches prims starting with "Visual" or "visual"
        r"^.*",                # Fallback: match all prims
    ],
)
```

## Working with Articulated Robots

USD files often contain articulated robots with multiple joints. Here's an example of loading and controlling a robot:

```python
import genesis as gs
from genesis.utils.misc import ti_to_numpy
import genesis.utils.geom as gu
import numpy as np

gs.init(backend=gs.cpu)

scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        dt=0.002,
        enable_collision=True,
        enable_joint_limit=True,
    ),
    show_viewer=True,
)

# Load USD robot
entities = scene.add_stage(
    morph=gs.morphs.USD(
        file="path/to/robot.usd",
    ),
)

scene.build()

# Access the rigid solver to control joints
rigid = scene.sim.rigid_solver
n_dofs = rigid.n_dofs

# Get joint limits
joint_limits = ti_to_numpy(rigid.dofs_info.limit)
joint_lower = joint_limits[:, 0]
joint_upper = joint_limits[:, 1]

# Set up PD control
rigid.set_dofs_kp(gu.default_dofs_kp(n_dofs))
rigid.set_dofs_kv(gu.default_dofs_kv(n_dofs))

# Control joint positions
for i in range(1000):
    # Example: sinusoidal joint motion
    t = scene.t * scene.dt
    target_positions = joint_lower + (joint_upper - joint_lower) * 0.5 * (1 + np.sin(t))
    rigid.control_dofs_position(target_positions)
    
    scene.step()
```

## Complete Example: Animated USD Scene

Here's a complete example that loads a USD file and animates its joints:

```python
import argparse
import numpy as np
from huggingface_hub import snapshot_download
import genesis as gs
from genesis.utils.misc import ti_to_numpy
import genesis.utils.geom as gu


class JointAnimator:
    """
    A simple JointAnimator to animate the joints' positions of the scene.
    
    It uses the sin function to interpolate between the lower and upper limits of the joints.
    """
    
    def __init__(self, scene: gs.Scene):
        self.rigid = scene.sim.rigid_solver
        n_dofs = self.rigid.n_dofs
        joint_limits = ti_to_numpy(self.rigid.dofs_info.limit)
        joint_limits = np.clip(joint_limits, -np.pi, np.pi)
        
        init_positions = self.rigid.get_dofs_position().numpy()
        
        self.joint_lower = joint_limits[:, 0]
        self.joint_upper = joint_limits[:, 1]
        
        valid_range_mask = (self.joint_upper - self.joint_lower) > gs.EPS
        
        normalized_init_pos = np.where(
            valid_range_mask,
            2.0 * (init_positions - self.joint_lower) / (self.joint_upper - self.joint_lower) - 1.0,
            0.0,
        )
        self.init_phase = np.arcsin(normalized_init_pos)
        
        # Make the control more sensitive
        self.rigid.set_dofs_frictionloss(gu.default_dofs_kp(n_dofs))
        self.rigid.set_dofs_kp(gu.default_dofs_kp(n_dofs))
    
    def animate(self, scene: gs.Scene):
        t = scene.t * scene.dt
        theta = np.pi * t + self.init_phase
        theta = theta % (2 * np.pi)
        sin_values = np.sin(theta)
        normalized = (sin_values + 1.0) / 2.0
        target = self.joint_lower + (self.joint_upper - self.joint_lower) * normalized
        self.rigid.control_dofs_position(target)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_steps", type=int, default=1000)
    parser.add_argument("-v", "--vis", action="store_true", default=False)
    args = parser.parse_args()
    
    gs.init(backend=gs.cpu)
    
    dt = 0.002
    scene = gs.Scene(
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(3.5, 0.0, 2.5),
            camera_lookat=(0.0, 0.0, 0.5),
            camera_fov=40,
        ),
        rigid_options=gs.options.RigidOptions(
            dt=dt,
            gravity=(0, 0, -9.8),
            enable_collision=True,
            enable_joint_limit=True,
            max_collision_pairs=1000,
        ),
        show_viewer=args.vis,
    )
    
    # Download USD asset
    asset_path = snapshot_download(
        repo_type="dataset",
        repo_id="Genesis-Intelligence/assets",
        revision="main",
        allow_patterns="usd/Refrigerator055/*",
        max_workers=1,
    )
    
    # Load USD stage
    entities = scene.add_stage(
        morph=gs.morphs.USD(
            file=f"{asset_path}/usd/Refrigerator055/Refrigerator055.usd",
        ),
    )
    
    scene.build()
    
    # Animate joints
    joint_animator = JointAnimator(scene)
    
    for _ in range(args.num_steps):
        joint_animator.animate(scene)
        scene.step()


if __name__ == "__main__":
    main()
```

## Supported USD Features

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

- Visual meshes (for rendering)
- Collision meshes (for physics simulation)
- Automatic mesh decimation
- Convex decomposition for collision detection

## Tips and Best Practices

### 1. **Isaac Sim Compatibility**

If you're using assets from NVIDIA Isaac Sim, the default attribute name candidates should be enough. They are:


- `physxJoint:jointFriction`
- `physxJoint:armature`
- `physxLimit:angular:stiffness`
- `physxLimit:angular:damping`
- `physxLimit:linear:stiffness`
- `physxLimit:linear:damping`
- `physxLimit:X:stiffness`
- `physxLimit:X:damping`
- `physxLimit:Y:stiffness`
- `physxLimit:Y:damping`
- `physxLimit:Z:stiffness`
- `physxLimit:Z:damping`
- `physics:jointFriction`
- `physics:armature`
- `physics:stiffness`
- `physics:angular:damping`
- `physics:linear:stiffness`
- `physics:linear:damping`


### 2. **Mesh Processing**

For better simulation performance, consider:

```python
gs.morphs.USD(
    file="complex_robot.usd",
    decimate=True,              # Simplify meshes
    decimate_face_num=500,      # Target face count
    convexify=True,             # Enable convex decomposition
    decompose_object_error_threshold=0.15,  # Balance accuracy vs performance
)
```

### 3. **Joint Control**

After loading a USD file, you can access and control joints through the rigid solver:

```python
scene.build()

rigid = scene.sim.rigid_solver

# Get current joint positions
positions = rigid.get_dofs_position().numpy()

# Get joint limits
limits = ti_to_numpy(rigid.dofs_info.limit)

# Control joints
rigid.control_dofs_position(target_positions)
rigid.control_dofs_velocity(target_velocities)
rigid.control_dofs_force(target_forces)
```

### 4. **Multiple Entities**

A single USD file can contain multiple entities. The `add_stage()` method returns a list of entities:

```python
entities = scene.add_stage(
    morph=gs.morphs.USD(file="scene.usd"),
)

# entities is a list of RigidEntity objects
for entity in entities:
    print(f"Entity: {entity.name}")
    print(f"Number of links: {len(entity.links)}")
    print(f"Number of joints: {len(entity.joints)}")
```

### 5. **Visualization Modes**

You can choose to visualize collision meshes instead of visual meshes:

```python
entities = scene.add_stage(
    morph=gs.morphs.USD(file="robot.usd"),
    vis_mode="collision",  # Use collision meshes for visualization
)
```

## Limitations and Notes

1. **Unit System**: Arbitrary unit system is not supported. We only support SI units (meters and kilograms).

2. **Scaling**: A programmatic scaling factor of the scene from the USD file is not supported. It is always assumed to be 1.0, but users can edit the scene root transform by themselves.

## Next Steps

- Learn about [controlling robots](control_your_robot.md) in Genesis
- Explore [inverse kinematics](inverse_kinematics_motion_planning.md) for USD-loaded robots
- Check out [parallel simulation](parallel_simulation.md) for training with USD assets
- See the [API reference](../../api_reference/options/morph/file_morph/file_morph.md) for detailed USD morph options

