# Constants & Enums

Genesis defines several enums and constants for physics simulation configuration.

## Backend Selection

```python
import genesis as gs

# Available backends
gs.backend.cpu      # CPU backend
gs.backend.gpu      # Auto-select GPU (CUDA on Linux, Metal on macOS)
gs.backend.cuda     # NVIDIA CUDA
gs.backend.metal    # Apple Metal
gs.backend.vulkan   # Vulkan
gs.backend.opengl   # OpenGL

# Usage
gs.init(backend=gs.gpu)
```

## Joint Types

```python
# Joint types for articulated bodies
gs.JOINT_TYPE.FIXED      # Fixed/welded joint (0 DOF)
gs.JOINT_TYPE.REVOLUTE   # Revolute/hinge joint (1 DOF)
gs.JOINT_TYPE.PRISMATIC  # Prismatic/slider joint (1 DOF)
gs.JOINT_TYPE.SPHERICAL  # Ball joint (3 DOF)
gs.JOINT_TYPE.FREE       # Free joint (6 DOF)
```

## Geometry Types

```python
# Geometry types for collision shapes
gs.GEOM_TYPE.PLANE      # Infinite plane
gs.GEOM_TYPE.SPHERE     # Sphere
gs.GEOM_TYPE.ELLIPSOID  # Ellipsoid
gs.GEOM_TYPE.CYLINDER   # Cylinder
gs.GEOM_TYPE.CAPSULE    # Capsule
gs.GEOM_TYPE.BOX        # Box
gs.GEOM_TYPE.MESH       # Mesh
gs.GEOM_TYPE.TERRAIN    # Heightfield terrain
```

## Control Modes

```python
# Control modes for joints
gs.CTRL_MODE.FORCE      # Force/torque control
gs.CTRL_MODE.VELOCITY   # Velocity control
gs.CTRL_MODE.POSITION   # Position control
```

## Integrators

```python
# Rigid body integrators
gs.integrator.Euler                    # Explicit Euler
gs.integrator.implicitfast             # Implicit fast
gs.integrator.approximate_implicitfast # Approximate implicit

# Usage
rigid_options = gs.options.RigidOptions(
    integrator=gs.integrator.implicitfast,
)
```

## Constraint Solvers

```python
# Constraint solving methods
gs.constraint_solver.CG      # Conjugate Gradient
gs.constraint_solver.Newton  # Newton's method

# Usage
rigid_options = gs.options.RigidOptions(
    constraint_solver=gs.constraint_solver.Newton,
)
```

## Image Types

```python
# Camera output types
gs.IMAGE_TYPE.RGB           # Color image
gs.IMAGE_TYPE.DEPTH         # Depth map
gs.IMAGE_TYPE.SEGMENTATION  # Segmentation mask
gs.IMAGE_TYPE.NORMAL        # Surface normals
```

## Equality Constraints

```python
# Equality constraint types (for MJCF)
gs.EQUALITY_TYPE.CONNECT  # Connect constraint
gs.EQUALITY_TYPE.WELD     # Weld constraint
gs.EQUALITY_TYPE.JOINT    # Joint equality
```

## See Also

- {doc}`device` - Device and platform utilities
- {doc}`/api_reference/options/index` - Configuration options
