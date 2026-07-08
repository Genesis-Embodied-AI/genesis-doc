# Mesh processing

Every mesh you load into Genesis World serves two different jobs, and they want opposite things. The **visual mesh** should look right, so it keeps every triangle the artist authored. The **collision mesh** feeds the physics solver, which is fastest and most stable when geometry is simple, watertight, and convex. A raw mesh from a scanner or an art tool is usually none of those things.

To bridge the gap, Genesis processes the collision geometry of a rigid entity automatically when you load it — watertightening, decimating, and convex-decomposing it — while leaving the visual mesh untouched. This page explains what that pipeline does, the options that control it, and when to reach for each one.

The two runnable examples referenced throughout are the source of truth for the code:

- [`examples/rigid/nonconvex_mesh.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/nonconvex_mesh.py) — loading a mesh and seeing objects rest on it.
- [`examples/rigid/convex_decomposition.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/convex_decomposition.py) — collision behavior of decomposed meshes.

## Loading a mesh

A non-articulated mesh is loaded through `gs.morphs.Mesh`, which accepts `.obj`, `.stl`, `.glb`, and `.gltf` files (see {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` for the morph basics and {doc}`Conventions </user_guide/getting_started/conventions>` for Y-up versus Z-up handling):

```python
import genesis as gs

tank = scene.add_entity(
    gs.morphs.Mesh(
        file="meshes/tank.obj",
        scale=5.0,
        fixed=True,
    ),
    vis_mode="collision",  # render the processed collision mesh instead of the visual mesh
)
```

The `vis_mode` shortcut is how you inspect the result of processing. It renders either `"visual"` (the default) or `"collision"` geometry, so you can see exactly what the solver sees.

:::{note}
The processing described below applies when the morph becomes a `RigidEntity`. Deformable entities (FEM, MPM, and other particle-based materials) do not convexify their meshes; see {doc}`Beyond rigid bodies </user_guide/getting_started/beyond_rigid_bodies>`.
:::

## The collision pipeline

When a mesh becomes a rigid entity, Genesis prepares its collision geometry in three stages:

- **Watertighten:** close gaps and remove non-manifold artifacts so the mesh bounds a well-defined volume. Controlled by `watertighten` (an integer 0–8, default 7).
- **Decimate:** reduce the triangle count toward a target so narrow-phase collision stays cheap.
- **Convexify:** replace the mesh with one or more convex hulls, since the collision solver is fastest and most robust on convex shapes.

Decimation and convexification are on by default for rigid entities and can be disabled independently. The visual mesh is never modified by any of this.

## Decimation

High-poly collision meshes slow down collision detection and can hurt numerical stability. Decimation collapses triangles down to a target count:

```python
gs.morphs.Mesh(
    file="high_poly.obj",
    decimate=True,
    decimate_face_num=500,       # target triangle count
    decimate_aggressiveness=2,   # 0 (lossless) to 8 (target at all costs)
)
```

- **`decimate`:** defaults to `True` when `convexify` is `True`, and `False` otherwise — a non-convex collision mesh is usually kept precisely because it has surface detail worth preserving.
- **`decimate_face_num`:** the target triangle count, default 500. Keep it above 100; below that, too much geometry is lost to be reliable.
- **`decimate_aggressiveness`:** how hard the simplifier works to hit the target, an integer 0–8 (default 2). At 0 it is lossless, at 2 it preserves all features, at 5 it may noticeably alter the shape, and at 8 it hits the target regardless of fidelity.

If you load a mesh with more than 5000 faces without decimating, Genesis warns you and suggests `decimate=True`.

## Convex decomposition

The collision solver treats every collision shape as convex. A single convex hull is enough for a mug or a box, but a concave shape — a bowl, a tank hull, a tool with a handle — would lose its cavities if wrapped in one hull. Convex decomposition instead splits the mesh into a set of convex pieces that together approximate the original, using the [CoACD](https://github.com/SarahWeiii/CoACD) library.

```python
gs.morphs.Mesh(
    file="concave.obj",
    convexify=True,
)
```

`convexify` defaults to `True` for rigid entities and `False` for deformable ones. Genesis does not always run a full decomposition, though: it first compares the volume of the raw mesh against its single convex hull, and if the difference is small enough, it keeps the cheaper hull. Two thresholds govern that decision:

- **`decompose_object_error_threshold`:** relative volume error below which a basic rigid object skips decomposition and uses its convex hull. Default 0.15 (15%). Set to `0.0` to force decomposition, `float("inf")` to disable it.
- **`decompose_robot_error_threshold`:** the same threshold for poly-articulated robots. Default `float("inf")`, so robot links are convexified to a single hull unless you lower it.

:::{note}
The older `decompose_nonconvex` argument is deprecated. Use `convexify` together with the two `decompose_*_error_threshold` options instead.
:::

### Tuning CoACD

When a full decomposition does run, pass a `gs.options.CoacdOptions` to control the quality-versus-count trade-off:

```python
gs.morphs.Mesh(
    file="concave.obj",
    convexify=True,
    coacd_options=gs.options.CoacdOptions(
        threshold=0.05,       # lower = tighter fit, more hulls
        max_convex_hull=-1,   # -1 = no cap on the number of hulls
        resolution=1000,      # sampling resolution of the decomposition
        preprocess_mode="auto",
    ),
)
```

The options that matter most in practice:

| Option | Default | Effect |
|---|---|---|
| `threshold` | `0.1` | Concavity tolerance. Halving it roughly doubles the number of hulls. |
| `max_convex_hull` | `-1` | Upper bound on the number of hulls; `-1` means no cap. |
| `resolution` | `1000` | Sampling resolution used during decomposition. |
| `preprocess_mode` | `"auto"` | Manifold preprocessing: `"auto"`, `"on"`, or `"off"`. |

See the [CoACD documentation](https://github.com/SarahWeiii/CoACD) for the full parameter set.

## Meshes for deformable simulation

Deformable solvers need a volumetric mesh, not a surface. When a mesh drives an FEM entity, Genesis tetrahedralizes it — filling the interior with tetrahedra — after an isotropic remeshing pass that regularizes edge lengths so the tetrahedralization is well-conditioned. This happens automatically:

```python
entity = scene.add_entity(
    morph=gs.morphs.Mesh(file="model.obj"),
    material=gs.materials.FEM.Elastic(E=1e5, nu=0.4),  # E in Pa, nu dimensionless
)
```

For the material side of deformable simulation, see {doc}`Soft robots </user_guide/getting_started/soft_robots>`.

## Caching

Mesh processing is expensive, so Genesis caches each result on disk keyed by a SHA-256 hash of the input geometry and the options that produced it. Change a relevant option and the key changes, so the stale entry is bypassed and the mesh is reprocessed. Subsequent loads with identical inputs read straight from cache.

| Result | Extension | Produced by |
|---|---|---|
| Convex decomposition | `.cvx` | Convexification |
| Tetrahedral mesh | `.tet` | FEM tetrahedralization |
| Signed distance field | `.gsd` | SDF-based collision |
| Remeshed surface | `.rm` | Remeshing for tetrahedralization |
| Particle samples | `.ptc` | Particle sampling |

## See also

- {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` — morphs, file formats, and loading entities.
- {doc}`Conventions </user_guide/getting_started/conventions>` — coordinate frames and Y-up versus Z-up mesh handling.
- {doc}`Beyond rigid bodies </user_guide/getting_started/beyond_rigid_bodies>` — deformable and particle-based materials.
