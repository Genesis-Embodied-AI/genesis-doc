# Geometry utilities

The `genesis.utils.geom` module provides geometry helpers for rotations, quaternions, and rigid transforms, also exposed at the top level as `gs.<name>`. They accept NumPy arrays or PyTorch tensors and operate on single values or batches.

They follow the project conventions: quaternions are `(w, x, y, z)` scalar-first (Hamilton), Euler angles are degrees in extrinsic x-y-z order, and the world frame is right-handed and Z-up. See {doc}`/user_guide/configuration/conventions`.

## Rotation conversions

```{eval-rst}
.. autofunction:: genesis.utils.geom.euler_to_quat
.. autofunction:: genesis.utils.geom.euler_to_R
.. autofunction:: genesis.utils.geom.xyz_to_quat
.. autofunction:: genesis.utils.geom.quat_to_xyz
.. autofunction:: genesis.utils.geom.quat_to_R
.. autofunction:: genesis.utils.geom.R_to_quat
.. autofunction:: genesis.utils.geom.R_to_xyz
.. autofunction:: genesis.utils.geom.axis_angle_to_quat
.. autofunction:: genesis.utils.geom.axis_angle_to_R
.. autofunction:: genesis.utils.geom.quat_to_rotvec
.. autofunction:: genesis.utils.geom.rotvec_to_quat
```

## Quaternion operations

```{eval-rst}
.. autofunction:: genesis.utils.geom.inv_quat
.. autofunction:: genesis.utils.geom.transform_quat_by_quat
.. autofunction:: genesis.utils.geom.transform_by_quat
.. autofunction:: genesis.utils.geom.inv_transform_by_quat
.. autofunction:: genesis.utils.geom.slerp
.. autofunction:: genesis.utils.geom.identity_quat
.. autofunction:: genesis.utils.geom.random_quaternion
```

## Rigid transforms

```{eval-rst}
.. autofunction:: genesis.utils.geom.transform_by_trans_quat
.. autofunction:: genesis.utils.geom.inv_transform_by_trans_quat
.. autofunction:: genesis.utils.geom.trans_quat_to_T
.. autofunction:: genesis.utils.geom.T_to_trans_quat
.. autofunction:: genesis.utils.geom.trans_R_to_T
.. autofunction:: genesis.utils.geom.transform_by_T
.. autofunction:: genesis.utils.geom.inv_transform_by_T
.. autofunction:: genesis.utils.geom.pos_lookat_up_to_T
```

## Vectors and sampling

```{eval-rst}
.. autofunction:: genesis.utils.geom.normalize
.. autofunction:: genesis.utils.geom.spherical_to_cartesian
.. autofunction:: genesis.utils.geom.generate_grid_points_on_plane
.. autofunction:: genesis.utils.geom.generate_ring_points_on_sphere
.. autoclass:: genesis.utils.geom.SpatialHasher
    :members:
```

## See also

- {doc}`/user_guide/configuration/conventions`: coordinate frame, rotation, and quaternion conventions.
- {doc}`tensor_utils`: converting between NumPy, PyTorch, and Genesis tensors.
