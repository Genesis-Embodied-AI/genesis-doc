# File I/O utilities

Genesis World provides utilities for file operations, path handling, and loading robot/scene descriptions.

## Cache and source directories

Genesis World caches compiled kernels and processed assets. These helpers, exposed under `gs.utils`, resolve the cache, source, and asset directories.

```{eval-rst}
.. autofunction:: genesis.utils.misc.get_cache_dir
.. autofunction:: genesis.utils.misc.get_gsd_cache_dir
.. autofunction:: genesis.utils.misc.get_src_dir
.. autofunction:: genesis.utils.misc.get_assets_dir
.. autofunction:: genesis.utils.misc.clear_caches
```

## Loading models and meshes

Robot descriptions and meshes are loaded by passing a file-based morph (`gs.morphs.URDF`, `gs.morphs.MJCF`, `gs.morphs.Mesh`, `gs.morphs.USD`) to `scene.add_entity(...)`. Supported mesh formats:

| Format | Extension | Notes |
|--------|-----------|-------|
| OBJ | `.obj` | Wavefront OBJ |
| STL | `.stl` | Stereolithography |
| GLB/GLTF | `.glb`, `.gltf` | GL Transmission Format |
| DAE | `.dae` | COLLADA |
| USD | `.usd`, `.usda`, `.usdc`, `.usdz` | Universal Scene Description (via `gs.morphs.USD`) |

For usage, see {doc}`/user_guide/assets/loading_assets`. Each morph and its options are documented under {doc}`/api_reference/engine/entity/morph/file_morph/index`.

## Asset paths

Genesis World resolves a morph's `file` in order:

1. Absolute path (if provided)
2. Relative to current working directory
3. Genesis World assets directory

## See also

- {doc}`/user_guide/assets/loading_assets`: loading robot descriptions and meshes
- {doc}`/api_reference/engine/entity/morph/file_morph/index`: File-based morphs
- {doc}`/api_reference/engine/entity/index`: Entity loading
