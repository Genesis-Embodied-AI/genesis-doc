# Geometry Utilities

Genesis provides utility functions for geometric transformations and calculations.

## Quaternion Operations

Genesis uses `(x, y, z, w)` quaternion convention (scalar-last).

```python
import genesis.utils.geom as gu
import numpy as np

# Create rotation quaternion (axis-angle)
axis = np.array([0, 0, 1])  # Z-axis
angle = np.pi / 2  # 90 degrees
quat = gu.axis_angle_to_quat(axis, angle)

# Quaternion multiplication
q1 = np.array([0, 0, 0, 1])  # Identity
q2 = np.array([0, 0, 0.707, 0.707])  # 90 deg around Z
q_combined = gu.quat_mul(q1, q2)

# Inverse quaternion
q_inv = gu.quat_inv(quat)

# Quaternion to rotation matrix
rot_matrix = gu.quat_to_matrix(quat)
```

## Transform Operations

```python
import genesis.utils.geom as gu

# Transform point by quaternion
point = np.array([1, 0, 0])
quat = np.array([0, 0, 0.707, 0.707])
rotated = gu.transform_by_quat(point, quat)

# Transform point by translation and quaternion
pos = np.array([1, 2, 3])
transformed = gu.transform_by_trans_quat(point, pos, quat)

# Inverse transform
original = gu.inv_transform_by_trans_quat(transformed, pos, quat)
```

## Rotation Conversions

```python
import genesis.utils.geom as gu

# Euler to quaternion (XYZ convention)
euler = np.array([0, 0, np.pi/2])  # Roll, Pitch, Yaw
quat = gu.euler_to_quat(euler)

# Quaternion to Euler
euler_back = gu.quat_to_euler(quat)

# Rotation matrix to quaternion
R = np.eye(3)
quat = gu.matrix_to_quat(R)
```

## Vector Operations

```python
import genesis.utils.geom as gu

# Normalize vector
v = np.array([1, 2, 3])
v_normalized = gu.normalize(v)

# Cross product
a = np.array([1, 0, 0])
b = np.array([0, 1, 0])
cross = gu.cross(a, b)

# Angle between vectors
angle = gu.angle_between(a, b)
```

## Common Patterns

### Setting Entity Orientation

```python
import genesis as gs
import genesis.utils.geom as gu
import numpy as np

gs.init()
scene = gs.Scene()
box = scene.add_entity(gs.morphs.Box(pos=(0, 0, 0.5)))
scene.build()

# Rotate 45 degrees around Z
angle = np.pi / 4
quat = gu.axis_angle_to_quat([0, 0, 1], angle)
box.set_quat(quat)
```

### Camera Look-at Calculation

```python
import genesis.utils.geom as gu

camera_pos = np.array([3, 0, 2])
target = np.array([0, 0, 0.5])

# Calculate look-at direction
direction = target - camera_pos
direction = direction / np.linalg.norm(direction)
```

## See Also

- {doc}`tensor_utils` - Tensor conversions
- {doc}`/api_reference/entity/index` - Entity transforms
