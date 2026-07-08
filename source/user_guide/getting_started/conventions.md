# Conventions

This page defines the coordinate system, rotation, and asset-import conventions that Genesis World uses throughout its API. State them the same way everywhere in your own code, and Genesis World will behave predictably.

## Coordinate system

Genesis World uses a right-handed, Z-up coordinate system. Relative to the default viewer, whose camera sits on the `+X` side looking back toward the origin:

- **+X**: points out of the screen, toward the viewer.
- **+Y**: points to the viewer's right.
- **+Z**: points up.

## Quaternion representation

Quaternions follow the `(w, x, y, z)` convention:

- **w**: scalar (real) component.
- **x, y, z**: vector (imaginary) components.

This is the scalar-first Hamilton convention. Whenever an API takes a quaternion, provide it in this order.

```python
# 90-degree rotation about the +Z axis
quat = (0.707, 0.0, 0.0, 0.707)  # (w, x, y, z)
```

Euler angles, where they are accepted instead, are extrinsic x-y-z in degrees (SciPy's convention).

## Gravity

Gravity defaults to `(0, 0, -9.81)`, i.e. `-Z` with a magnitude of 9.81 m/s². With no other forces applied, objects fall along `-Z`. Set it per scene through `gs.options.SimOptions(gravity=...)`.

## Axis conversion at import time

Different 3D asset formats define, or omit, their coordinate-system conventions. Genesis World applies precise rules to bring every imported mesh into its internal Z-up representation. The following sections describe how each supported format is handled.

### Alignment with Blender exporters

Genesis World's mesh import behavior is aligned with Blender's default exporter settings. Blender is a common authoring tool for robotics and simulation assets, and its exporters apply well-defined axis conversions depending on the target format (for example, converting from Blender's internal Z-up space to glTF's Y-up convention on export).

By mirroring Blender's exporter behavior:

- Assets exported from Blender with default settings import into Genesis World with the expected orientation.
- You can rely on Blender's preview and transforms without format-specific workarounds.
- Cross-format consistency (glTF, STL, OBJ, and URDF-referenced meshes) is preserved.

### Y-up and Z-up are not a single convention

There is no single, universal transformation between Y-up and Z-up. A Y-up-to-Z-up conversion is a 3×3 rotation, and several valid rotations exist depending on how the remaining axes (typically forward and right) are mapped. Two assets can both be labeled "Y-up" yet differ in orientation because they chose different forward axes.

So labeling an asset "Y-up" or "Z-up" is not enough to define its spatial convention; the forward-axis choice determines the rotation.

#### Genesis World convention

Genesis World adopts one specific Y-up-to-Z-up mapping, aligned with Blender's exporter behavior. Blender's internal coordinate system is Z-up, and its exporters let you choose any combination of up and forward vectors when writing a Y-up format. Genesis World adopts Blender's default Y-up exporter configuration: **Y-up, −Z forward**. Concretely, a Y-up mesh is converted to Z-up by mapping `(X, Y, Z) → (X, -Z, Y)`. This ensures that:

- Assets exported from Blender with default axis settings appear identical in Genesis World.
- The rotation used is consistent across formats.
- Axis-conversion behavior is predictable and reproducible.

Every reference to "Y-up" handling in Genesis World means this specific Blender-aligned representation, not an abstract or ambiguous Y-up.

### glTF (.gltf, .glb)

glTF assets are [always Y-up by specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#coordinate-system-and-units). On import, Genesis World converts glTF meshes from Y-up to Z-up. This conversion is fixed and cannot be disabled, guaranteeing that imported meshes end up in Genesis World's Z-up space and that the result complies with the glTF specification.

Blender can also export a glTF as Z-up by unchecking the **+Y-up** option, but it cannot reimport such a file correctly. Because Genesis World's glTF conversion is fixed to Y-up, a Z-up-exported glTF imports with the wrong orientation. Re-export the asset with the default **+Y-up** option rather than relying on axis overrides.

![Blender glTF exporter panel with the +Y-up transform option enabled](images/blender_gltf_export.png)

See [Blender's glTF exporter documentation](https://docs.blender.org/manual/en/2.83/addons/import_export/scene_gltf2.html#transform) for the transform settings.

### STL (.stl) and Wavefront OBJ (.obj)

STL and OBJ do not define a standard coordinate system, so the up-axis must be specified explicitly at import. Assets in these formats may be either Y-up or Z-up, depending on the originating tool. Genesis World lets you declare how to interpret them:

- **Z-up (default):** the mesh is assumed to already be in Z-up space, and no conversion is applied.
- **Y-up:** the mesh is assumed to be Y-up, and the `(X, Y, Z) → (X, -Z, Y)` conversion above is applied.

This lets you import STL and OBJ assets from different sources correctly without modifying the original files.

![Blender Wavefront OBJ exporter panel showing the up-axis and forward-axis settings](images/blender_yup_export.png)

See [Blender's Wavefront OBJ exporter](https://docs.blender.org/manual/en/4.0/files/import_export/obj.html#object-properties) and [Blender's STL exporter](https://docs.blender.org/manual/fr/3.6/addons/import_export/mesh_stl.html#transform) documentation.

### Declaring the up-axis on import

Pass `file_meshes_are_zup` to a mesh morph to tell Genesis World how the referenced meshes are oriented. It defaults to `True` (already Z-up); set it to `False` for a Y-up asset that needs conversion:

```python
obj = scene.add_entity(
    gs.morphs.Mesh(
        file="my_obj_file.obj",
        file_meshes_are_zup=False,  # mesh is Y-up; convert to Z-up on import
    ),
)
```

After import, each mesh records whether a conversion was applied in its `imported_as_zup` metadata flag:

```python
obj.vgeoms[0].mesh.metadata["imported_as_zup"]  # False if a Y-up -> Z-up conversion ran
```
