# Geometry utilities

Genesis World ships a library of geometry helpers for rotations, quaternions, and rigid transforms. They are exposed both at the top level as `gs.<name>` and under `genesis.utils.geom`, and they accept NumPy arrays or PyTorch tensors, operating on single values or batches. Use them to build poses, convert between rotation representations, and transform points between frames.

All of them follow the project conventions: quaternions are `(w, x, y, z)` scalar-first (Hamilton), `euler_to_quat` and `euler_to_R` take degrees in extrinsic x-y-z order, and the world frame is right-handed and Z-up. See {doc}`/user_guide/configuration/conventions` for the full set.

```python
import genesis as gs

gs.init()

# Euler (degrees, extrinsic x-y-z) to quaternion (w, x, y, z)
quat = gs.euler_to_quat((0, 0, 90))

# Rotate a point by a quaternion
p_world = gs.transform_by_quat((1.0, 0.0, 0.0), quat)

# Apply a full rigid transform: rotate then translate
p_world = gs.transform_by_trans_quat((1.0, 0.0, 0.0), trans=(0, 0, 1), quat=quat)
```

## Rotation conversions

Rotations can be expressed as Euler angles, quaternions, 3×3 matrices, rotation vectors, or 4×4 homogeneous transforms. These convert between them.

| Function | Converts |
|---|---|
| `euler_to_quat(euler_xyz)` | Euler degrees (extrinsic x-y-z) to quaternion |
| `euler_to_R(euler_xyz)` | Euler degrees to 3×3 rotation matrix |
| `xyz_to_quat(xyz, rpy=False, degrees=False)` | Euler angles to quaternion, with unit and order options |
| `quat_to_xyz(quat, rpy=False, degrees=False)` | Quaternion to Euler angles |
| `quat_to_R(quat)` / `R_to_quat(R)` | Quaternion ↔ rotation matrix |
| `R_to_xyz(R, rpy=False, degrees=False)` | Rotation matrix to Euler angles |
| `axis_angle_to_quat(angle, axis)` / `axis_angle_to_R(axis, theta)` | Axis-angle to quaternion or matrix |
| `quat_to_rotvec(quat)` / `rotvec_to_quat(rotvec)` | Quaternion ↔ rotation vector (axis × angle) |

:::{note}
Argument order differs between `axis_angle_to_quat(angle, axis)` (angle first) and `axis_angle_to_R(axis, theta)` (axis first).
:::

## Quaternion operations

| Function | Result |
|---|---|
| `inv_quat(quat)` | Inverse (conjugate for unit quaternions) |
| `transform_quat_by_quat(v, u)` | Quaternion product, composing rotation `v` by `u` |
| `transform_by_quat(v, quat)` | Rotate vector `v` by `quat` |
| `inv_transform_by_quat(pos, quat)` | Rotate `pos` by the inverse of `quat` |
| `slerp(q0, q1, t)` | Spherical linear interpolation at fraction `t` |
| `identity_quat()` | The identity quaternion `(1, 0, 0, 0)` |

## Rigid transforms

A rigid transform is a rotation plus a translation, stored either as a `(trans, quat)` pair or as a 4×4 homogeneous matrix `T`.

| Function | Result |
|---|---|
| `transform_by_trans_quat(pos, trans, quat)` | Rotate `pos` by `quat`, then add `trans` |
| `inv_transform_by_trans_quat(pos, trans, quat)` | Inverse of the above |
| `trans_quat_to_T(trans, quat)` / `T_to_trans_quat(T)` | `(trans, quat)` ↔ 4×4 matrix |
| `trans_R_to_T(trans, R)` | Build a 4×4 matrix from translation and rotation matrix |
| `transform_by_T(pos, T)` / `inv_transform_by_T(pos, T)` | Apply `T` (or its inverse) to `pos` |
| `pos_lookat_up_to_T(pos, lookat, up)` | Camera extrinsics: eye, target, up to a 4×4 matrix |

## Vectors

| Function | Result |
|---|---|
| `normalize(x, eps=1e-12)` | Scale a vector or batch to unit length |
| `spherical_to_cartesian(theta, phi)` | Spherical angles to a unit `(x, y, z)` direction |

## See also

- {doc}`/user_guide/configuration/conventions`: coordinate frame, rotation, and quaternion conventions
- {doc}`tensor_utils`: converting between NumPy, PyTorch, and Genesis tensors
