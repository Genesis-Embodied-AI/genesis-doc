# Geometry Utilities

Genesis 提供用于几何变换和计算的工具函数。

## Quaternion 操作

Genesis 使用 `(x, y, z, w)` 四元数约定（标量在后）。

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

## Transform 操作

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

## Rotation 转换

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

## Vector 操作

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

## 常见模式

### 设置实体方向

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

### 相机 Look-at 计算

```python
import genesis.utils.geom as gu

camera_pos = np.array([3, 0, 2])
target = np.array([0, 0, 0.5])

# Calculate look-at direction
direction = target - camera_pos
direction = direction / np.linalg.norm(direction)
```

## 另请参阅

- {doc}`tensor_utils` - 张量转换
- {doc}`/api_reference/entity/index` - 实体变换
