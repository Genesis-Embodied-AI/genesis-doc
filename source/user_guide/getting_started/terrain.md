# Terrain

`gs.morphs.Terrain` adds a static rigid ground defined by a **height field**: a 2D grid of elevations. It is the standard ground for locomotion work: instead of a flat {py:class}`~genesis.options.morphs.Plane`, a robot walks over slopes, stairs, and obstacles. You build a terrain one of two ways: let Genesis World procedurally generate a grid of **sub-terrains**, or supply your own height field.

The three runnable examples referenced on this page ship with Genesis World:

- [`examples/rigid/terrain_subterrain.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/terrain_subterrain.py): procedural sub-terrain grid
- [`examples/rigid/terrain_height_field.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/terrain_height_field.py): a user-supplied height field
- [`examples/rigid/terrain_from_mesh.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/terrain_from_mesh.py): a height field derived from a triangle mesh

## Minimal example

The fewest lines that put a robot-scale terrain on the ground: a 2×2 grid of stair sub-terrains.

```python
import genesis as gs

gs.init(backend=gs.gpu)  # use gs.cpu to run anywhere

scene = gs.Scene(show_viewer=True)

terrain = scene.add_entity(
    gs.morphs.Terrain(
        n_subterrains=(2, 2),
        subterrain_size=(6.0, 6.0),  # meters, per tile
        subterrain_types="pyramid_stairs_terrain",
    ),
)

scene.build()
for _ in range(1000):
    scene.step()
```

A single string for `subterrain_types` is applied to every tile. The next sections cover how the height field is laid out and how to mix tile types, supply your own data, or derive one from a mesh.

## How a terrain is represented

A terrain is a static rigid entity backed by a height field: a 2D array `height_field[i, j]` of integer height samples on a regular grid. Two scales convert that grid into meters in the scene's right-handed, Z-up frame:

- `horizontal_scale`: meters between adjacent grid points (the cell size). Default `0.25`.
- `vertical_scale`: meters per height-field unit. Default `0.005`.

So grid cell `(i, j)` sits at world position `(i * horizontal_scale, j * horizontal_scale, height_field[i, j] * vertical_scale)`, offset by the morph's `pos`. Genesis World turns this grid into two representations at build time: a height map and SDF for collision queries, and a watertight triangle mesh for rendering.

:::{note}
The terrain's collision SDF resolution is computed automatically and ignores any resolution set on `gs.materials.Rigid()`.
:::

## Procedural sub-terrains

For locomotion, you rarely author a height field by hand. Instead, tile the ground with **sub-terrains** (the approach popularized by Isaac Gym), where each tile is filled by a named generator. Three parameters control the grid:

- `n_subterrains=(nx, ny)`: number of tiles in x and y. Default `(3, 3)`.
- `subterrain_size=(sx, sy)`: size of each tile in meters. Default `(12.0, 12.0)`.
- `subterrain_types`: a single generator name applied to all tiles, or a 2D list matching `n_subterrains`.

```python
terrain = scene.add_entity(
    gs.morphs.Terrain(
        n_subterrains=(2, 2),
        subterrain_size=(6.0, 6.0),
        horizontal_scale=0.25,  # meters per grid cell
        vertical_scale=0.005,  # meters per height unit
        subterrain_types=[
            ["flat_terrain", "random_uniform_terrain"],
            ["pyramid_sloped_terrain", "discrete_obstacles_terrain"],
        ],
    ),
)
```

The available generators:

| Generator | Produces |
|---|---|
| `flat_terrain` | A flat tile. |
| `random_uniform_terrain` | Uniform random bumps. |
| `sloped_terrain` | A single constant slope. |
| `pyramid_sloped_terrain` | Slopes rising to a central peak. |
| `discrete_obstacles_terrain` | Scattered raised/lowered blocks. |
| `wave_terrain` | Sinusoidal waves. |
| `stairs_terrain` | Parallel steps. |
| `pyramid_stairs_terrain` | Steps rising to a central platform. |
| `stepping_stones_terrain` | Isolated stones with gaps between them. |
| `fractal_terrain` | Fractal noise heightscape. |

Set `randomize=True` to give the generators that involve randomness fresh parameters on each build; left `False` (the default), they use a fixed seed so the terrain is reproducible. Per-generator settings can be overridden through `subterrain_parameters`.

## Custom height field

Pass a `height_field` array to build the terrain from your own data, for example a digital elevation model, or a NumPy array you generate. When `height_field` is set, the sub-terrain parameters above are ignored.

```python
import numpy as np

horizontal_scale = 0.25
vertical_scale = 0.005
height_field = np.zeros([40, 40])
heights_range = np.arange(-10, 20, 10)
height_field[5:35, 5:35] = 200 + np.random.choice(heights_range, (30, 30))

terrain = scene.add_entity(
    gs.morphs.Terrain(
        horizontal_scale=horizontal_scale,
        vertical_scale=vertical_scale,
        height_field=height_field,
    ),
)
```

Values are in height-field units, not meters: an entry of `200` with `vertical_scale=0.005` sits at `1.0 m`.

After the scene is built, the height field actually used is available on the terrain geometry as `terrain.geoms[0].metadata["height_field"]`. This is useful for verifying geometry, for instance drawing a debug sphere at every sample:

```python
height_field = terrain.geoms[0].metadata["height_field"]
rows = horizontal_scale * torch.arange(0, height_field.shape[0], device=gs.device)
cols = horizontal_scale * torch.arange(0, height_field.shape[1], device=gs.device)
rows = rows.unsqueeze(1).repeat((1, height_field.shape[1]))
cols = cols.unsqueeze(0).repeat((height_field.shape[0], 1))
heights = vertical_scale * torch.tensor(height_field, device=gs.device)
poss = torch.stack([rows, cols, heights], dim=-1).reshape((-1, 3))  # shape (n_cells, 3), meters
scene.draw_debug_spheres(poss=poss, radius=0.05, color=(0, 0, 1, 0.7))
```

## Height field from a mesh

If you already have a terrain as a triangle mesh, `genesis.utils.terrain.mesh_to_heightfield` samples it with vertical rays and returns a height field you can hand to `Terrain`. This trades the mesh's exact geometry for the fast collision queries of a height field.

```python
from genesis.utils.terrain import mesh_to_heightfield

horizontal_scale = 2.0  # target grid spacing, mesh units
# heights: (nx, ny); xs: (nx,); ys: (ny,)
hf_terrain, xs, ys = mesh_to_heightfield(path_terrain, spacing=horizontal_scale, oversample=1)

# The height field starts at the origin; shift it to sit under the mesh.
translation = np.array([np.nanmin(xs), np.nanmin(ys), 0.0])

terrain = scene.add_entity(
    morph=gs.morphs.Terrain(
        horizontal_scale=horizontal_scale,
        vertical_scale=1.0,  # heights are already in mesh units (meters)
        height_field=hf_terrain,
        pos=translation,
    ),
)
```

`spacing` is the grid step in the mesh's own units, and `oversample` casts extra rays per cell so peaks inside a cell are not missed (memory grows as `oversample²`). Pass `up_axis="y"` for meshes authored Y-up, such as glTF; the function rotates them to Z-up before sampling. Cells with no ray hit come back as `NaN`.

## Caching generated terrains

Generating a terrain (the height field, the collision mesh, and the visual mesh) runs every time the scene is built. Pass `name="my_terrain"` to generate it only once for a given set of options and load it from cache on later builds. This holds even when `randomize=True`, so it is the way to reconstruct a randomized terrain exactly across runs.

## See also

- {doc}`gs.morphs.Terrain API reference </api_reference/options/morph/file_morph/terrain>`: every keyword argument.
- {doc}`Hello, Genesis World <hello_genesis>`: the init–scene–build–step loop these examples assume.
- {doc}`Locomotion training <policy_training/examples/locomotion>`: training a walking policy, where terrain becomes the training ground.
