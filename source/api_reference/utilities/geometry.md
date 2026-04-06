# Geometry Utilities

Genesis provides utility functions for geometric transformations and calculations.

## Quaternion Operations

Genesis uses `(w, x, y, z)` quaternion convention (scalar-first).

```python
import numpy as np
import genesis.utils.geom as gu

# Create rotation quaternion (axis-angle)
axis = np.array([0.0, 0.0, 1.0])  # Z-axis
angle = np.array([np.pi / 2])  # 90 degrees
quat = gu.axis_angle_to_quat(angle, axis)

# Compose two rotations (quaternion multiplication)
q1 = np.array([1.0, 0.0, 0.0, 0.0])  # Identity
q2 = np.array([0.707, 0.0, 0.0, 0.707])  # 90 deg around Z
q_combined = gu.transform_quat_by_quat(q2, q1)

# Inverse quaternion
q_inv = gu.inv_quat(quat)

# Quaternion to rotation matrix
rot_matrix = gu.quat_to_R(quat)
```

## Transform Operations

```python
import numpy as np
import genesis.utils.geom as gu

# Transform point by quaternion
point = np.array([[1.0, 0.0, 0.0]])
quat = np.array([0.707, 0.0, 0.0, 0.707])
rotated = gu.transform_by_quat(point, quat)

# Transform point by translation and quaternion
pos = np.array([1.0, 2.0, 3.0])
transformed = gu.transform_by_trans_quat(point, pos, quat)

# Inverse transform
original = gu.inv_transform_by_trans_quat(transformed, pos, quat)
```

## Rotation Conversions

```python
import numpy as np
import genesis.utils.geom as gu

# Euler to quaternion (Roll, Pitch, Yaw in degrees)
euler = np.array([0, 0, 90])
quat = gu.euler_to_quat(euler)

# Quaternion to Euler (Roll, Pitch, Yaw in degrees)
euler_back = gu.quat_to_xyz(quat, rpy=True, degrees=True)

# Rotation matrix to quaternion
R = np.eye(3).reshape(1, 3, 3)
quat = gu.R_to_quat(R)
```

## Vector Operations

```python
import numpy as np
import genesis.utils.geom as gu

# Normalize vector
v = np.array([1, 2, 3])
v_normalized = gu.normalize(v)

# Get orthogonal basis from a normal vector
normal = gu.normalize(np.array([[0.0, 1.0, 1.0]]))
b, c = gu.orthogonals(normal)

# Spherical linear interpolation between quaternions
q0 = np.array([1.0, 0.0, 0.0, 0.0])  # Identity
q1 = np.array([0.707, 0.0, 0.0, 0.707])  # 90 deg around Z
t = np.array([0.5])  # Midpoint
q_mid = gu.slerp(q0, q1, t)
```

## Common Patterns

### Setting Entity Orientation

```python
import genesis as gs
import numpy as np
import genesis.utils.geom as gu

gs.init()
scene = gs.Scene()
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5), size=(1.0, 1.0, 1.0)))
scene.build()

# Rotate 45 degrees around Z
angle = np.array([np.pi / 4])
quat = gu.axis_angle_to_quat(angle, np.array([0.0, 0.0, 1.0]))
box.set_quat(quat)
```

### Camera Look-at Calculation

```python
import numpy as np
import genesis.utils.geom as gu

camera_pos = np.array([3.0, 0.0, 2.0])
target = np.array([0.0, 0.0, 0.5])

# Calculate look-at direction
direction = target - camera_pos
direction = direction / np.linalg.norm(direction)
```

## See Also

- {doc}`tensor_utils` - Tensor conversions
- {doc}`/api_reference/entity/index` - Entity transforms
