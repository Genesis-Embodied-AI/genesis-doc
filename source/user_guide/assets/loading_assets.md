# Loading assets

Almost everything you put in a scene, a robot, a rigid object, a static mesh, comes from an asset file loaded through a **morph**. A morph combines an entity's geometry with its initial pose, and you pass one as the first argument to `scene.add_entity(...)`. This page covers the supported formats, the pose and scale options common to all of them, and how Genesis World finds asset files.

## Supported formats

| Morph | Formats | Use for |
|---|---|---|
| {py:class}`gs.morphs.MJCF <genesis.options.morphs.MJCF>` | `.xml` | MuJoCo robot and scene models |
| {py:class}`gs.morphs.URDF <genesis.options.morphs.URDF>` | `.urdf`, `.xacro` | robot descriptions (`.xacro` is preprocessed automatically) |
| {py:class}`gs.morphs.Mesh <genesis.options.morphs.Mesh>` | `.obj`, `.stl`, `.dae`, `.glb`, `.gltf` | non-articulated meshes |
| {py:class}`gs.morphs.USD <genesis.options.morphs.USD>` | `.usd`, `.usda`, `.usdc`, `.usdz` | Universal Scene Description stages |

Shape primitives, {py:class}`gs.morphs.Plane <genesis.options.morphs.Plane>`, {py:class}`Box <genesis.options.morphs.Box>`, {py:class}`Cylinder <genesis.options.morphs.Cylinder>`, {py:class}`Sphere <genesis.options.morphs.Sphere>`, {py:class}`Terrain <genesis.options.morphs.Terrain>`, and {py:class}`Drone <genesis.options.morphs.Drone>`, need no file. See the {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` tutorial for a first load, {doc}`USD import </user_guide/assets/usd_import>` for USD stages, and {doc}`mesh processing </user_guide/assets/mesh_processing>` for preparing meshes.

```python
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
mug = scene.add_entity(
    gs.morphs.Mesh(file="meshes/mug.obj", scale=0.1),
)
```

## Pose and scale

Every morph accepts an initial pose and scale, so you rarely need to move an entity after adding it:

```python
scene.add_entity(
    gs.morphs.URDF(
        file="urdf/go2/urdf/go2.urdf",
        pos=(0, 0, 0.4),        # meters, world frame
        euler=(0, 0, 90),       # extrinsic x-y-z, degrees (SciPy convention)
        scale=1.0,
    ),
)
```

- **`pos`** is the position in meters, in the right-handed, Z-up world frame.
- **`euler`** sets orientation as extrinsic x-y-z angles in degrees; **`quat`** sets it as a `(w, x, y, z)` scalar-first quaternion instead. Set one or the other, not both.
- **`scale`** is a uniform factor. `gs.morphs.Mesh` also accepts a per-axis `(sx, sy, sz)` tuple.

See {doc}`/user_guide/configuration/conventions` for the coordinate frame, rotation, and unit conventions in full.

## Articulated bases: fixed or free

An MJCF file specifies the joint connecting a robot's base to the world, so its base is fixed or floating as authored. A URDF does not: its base is free (a 6-DoF joint to the world) unless you fix it. The same applies to `gs.morphs.Mesh`.

```python
# Bolt the robot's base to the world.
arm = scene.add_entity(gs.morphs.URDF(file="urdf/panda_bullet/panda.urdf", fixed=True))
```

For articulated models, two URDF options matter for performance and control:

- **`merge_fixed_links`** (default `True`) merges links joined by fixed joints into one rigid body, which is faster. If you need a merged link to stay addressable, for example an end-effector frame you drive with {doc}`inverse kinematics </user_guide/robot_control/inverse_kinematics_motion_planning>`, list it in **`links_to_keep`**.

## How file paths are resolved

A morph's `file` may be an absolute path or a relative one. A relative path is resolved first against your current working directory, and if nothing is found there, against the asset directory bundled with Genesis World (`genesis/assets`). That is why `file="xml/franka_emika_panda/panda.xml"` loads the Franka model that ships with the package without any path setup.

:::{note}
For MJCF and URDF, you can also pass inline XML content as `file` instead of a path. A string that parses as XML is used directly and skips path resolution.
:::

## See also

- {doc}`/api_reference/engine/entity/morph/index`: the full morph reference, with every per-format option.
- {doc}`/user_guide/assets/usd_import`: importing USD stages.
- {doc}`/user_guide/assets/mesh_processing`: convex decomposition, decimation, and other mesh preparation.
