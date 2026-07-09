# Constants and enums

Genesis World defines several enums and constants for physics simulation configuration.

## Backend selection

```python
import genesis as gs

# Available backends
gs.cpu      # CPU backend
gs.gpu      # auto-select GPU (CUDA on Linux, Metal on macOS)
gs.cuda     # NVIDIA CUDA
gs.metal    # Apple Metal
gs.amdgpu   # AMD ROCm (HIP)

# Usage
gs.init(backend=gs.gpu)
```

After `gs.init()`, `gs.backend` holds the backend that was actually selected.

## Joint types

```python
# Joint types for articulated bodies
gs.JOINT_TYPE.FIXED      # Fixed/welded joint (0 DOF)
gs.JOINT_TYPE.REVOLUTE   # Revolute/hinge joint (1 DOF)
gs.JOINT_TYPE.PRISMATIC  # Prismatic/slider joint (1 DOF)
gs.JOINT_TYPE.SPHERICAL  # Ball joint (3 DOF)
gs.JOINT_TYPE.FREE       # Free joint (6 DOF)
```

## Geometry types

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

## Control modes

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

## Constraint solvers

```python
# Constraint solving methods
gs.constraint_solver.CG      # Conjugate Gradient
gs.constraint_solver.Newton  # Newton's method

# Usage
rigid_options = gs.options.RigidOptions(
    constraint_solver=gs.constraint_solver.Newton,
)
```

## Broadphase traversal

```python
# Broadphase collision detection methods
gs.broadphase_traversal.SAP          # Sweep and Prune
gs.broadphase_traversal.ALL_VS_ALL   # Brute-force all pairs
```

## Parallelization level

```python
# Multi-environment parallelization levels
gs.PARA_LEVEL.NEVER    # No parallelization
gs.PARA_LEVEL.PARTIAL  # Partial parallelization
gs.PARA_LEVEL.ALL      # Full parallelization
```

## Equality constraints

```python
# Equality constraint types (for MJCF)
gs.EQUALITY_TYPE.CONNECT  # Connect constraint
gs.EQUALITY_TYPE.WELD     # Weld constraint
gs.EQUALITY_TYPE.JOINT    # Joint equality
```

## Entity state

```python
gs.ACTIVE    # Entity is active (1)
gs.INACTIVE  # Entity is inactive (0)
```

## See also

- {doc}`device`: Device and platform utilities
- {doc}`/api_reference/options/index`: Configuration options
