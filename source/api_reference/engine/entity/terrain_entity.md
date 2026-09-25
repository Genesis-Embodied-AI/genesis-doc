# TerrainEntity

A `TerrainEntity` is the rigid entity that `scene.add_entity(gs.morphs.Terrain(...))` returns. Its single fixed link is a height field, a grid of elevations that bodies rest on, and `get_terrain_height` reads the surface elevation at any point of it. For usage, see {doc}`/user_guide/physics/terrain`.

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.terrain_entity.TerrainEntity
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/physics/terrain`: building a terrain and querying its surface height.
- {doc}`/api_reference/engine/entity/morph/file_morph/terrain`: the `gs.morphs.Terrain` morph and its options.
