# Mesh utilities

The `genesis.utils.mesh` module provides helpers for loading meshes, generating primitive geometry, tetrahedralizing solids, and converting colors. They operate on `trimesh` meshes and NumPy arrays.

## Loading and decomposition

```{eval-rst}
.. autofunction:: genesis.utils.mesh.load_mesh
.. autofunction:: genesis.utils.mesh.convex_decompose
.. autofunction:: genesis.utils.mesh.merge_submeshes
```

## Primitive geometry

```{eval-rst}
.. autofunction:: genesis.utils.mesh.create_sphere
.. autofunction:: genesis.utils.mesh.create_cylinder
.. autofunction:: genesis.utils.mesh.create_cone
.. autofunction:: genesis.utils.mesh.create_box
.. autofunction:: genesis.utils.mesh.create_plane
.. autofunction:: genesis.utils.mesh.create_arrow
.. autofunction:: genesis.utils.mesh.create_line
.. autofunction:: genesis.utils.mesh.create_frame
.. autofunction:: genesis.utils.mesh.create_camera_frustum
```

## Tetrahedralization

```{eval-rst}
.. autofunction:: genesis.utils.mesh.tetrahedralize_mesh
.. autofunction:: genesis.utils.mesh.create_tets_mesh
```

## Color conversion

```{eval-rst}
.. autofunction:: genesis.utils.mesh.color_f32_to_u8
.. autofunction:: genesis.utils.mesh.color_u8_to_f32
.. autofunction:: genesis.utils.mesh.glossiness_to_roughness
```

## Mesh info

```{eval-rst}
.. autoclass:: genesis.utils.mesh.MeshInfo
    :members:
.. autoclass:: genesis.utils.mesh.MeshInfoGroup
    :members:
```

## See also

- {doc}`geom`: geometry transforms.
- {doc}`file_io`: loading meshes through file-based morphs.
