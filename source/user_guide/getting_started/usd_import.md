# Importing USD assets

[Universal Scene Description (USD)](https://openusd.org/) is Pixar's open framework for describing and composing 3D scenes. Genesis World imports USD files (`.usd`, `.usda`, `.usdc`, `.usdz`) through `gs.morphs.USD`, reading geometry, materials, and `UsdPhysics` joint definitions. A single file may hold one articulated robot, one rigid object, or a whole environment of many entities, like the assets that NVIDIA Isaac Sim and similar tools export.

Two runnable examples are the source of truth for this page:

- [`examples/usd/import_stage.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/usd/import_stage.py): load a single articulated asset and animate its joints.
- [`examples/usd/kitchen.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/usd/kitchen.py): load a multi-entity kitchen scene with per-asset processing options.

## Installation

USD parsing needs the `usd` optional dependency:

```bash
pip install -e ".[usd]"
```

That installs `usd-core`, which is enough to read USD files and their `UsdPreviewSurface` materials. For assets whose materials use other shaders, see [material baking](#material-baking) below.

## Minimal working example

The following loads a refrigerator asset and steps the simulation. It downloads the asset from the Genesis World asset repository on Hugging Face on first run:

```python
import genesis as gs
from huggingface_hub import snapshot_download

gs.init(backend=gs.cpu)

scene = gs.Scene(show_viewer=True)
scene.add_entity(gs.morphs.Plane())

asset_path = snapshot_download(
    repo_type="dataset",
    repo_id="Genesis-Intelligence/assets",
    revision="c50bfe3e354e105b221ef4eb9a79504650709dd2",
    allow_patterns="usd/Refrigerator055/*",
    max_workers=1,
)

entities = scene.add_stage(
    morph=gs.morphs.USD(
        file=f"{asset_path}/usd/Refrigerator055/Refrigerator055.usd",
        pos=(0, 0, 0.9),
        euler=(0, 0, 180),  # extrinsic x-y-z, degrees
    ),
)

scene.build()
for _ in range(1000):
    scene.step()
```

`add_stage` returns a `list` of the {doc}`entities </api_reference/entity/index>` it created, one per rigid body or articulation found in the file. The refrigerator is a single articulation, so the list has one element; a room scene returns many. See {doc}`hello_genesis` for the initialize / scene / build / step lifecycle that every Genesis World program shares.

## `add_stage` vs. `add_entity`

A USD file is a *stage* that can contain any number of physics entities. Genesis World offers two entry points:

- **`scene.add_stage(morph=gs.morphs.USD(...))`** discovers and loads **every** rigid entity in the file and returns them as a list. Use it for complete scenes and for any file whose contents you don't want to enumerate by hand.
- **`scene.add_entity(gs.morphs.USD(...))`** loads a **single** entity and returns it directly. It targets the prim named by `prim_path`; when `prim_path` is left as `None`, it falls back to the stage's default prim, and raises if the file declares none.

Both accept the same `gs.morphs.USD` morph, so every option below applies to either path.

## Articulations and rigid bodies

Genesis World parses `UsdPhysics` joints into a `dof` graph. Rigid bodies with no joints between them become free bodies; bodies connected by joints become one articulation. The supported joint types are:

| USD schema | Genesis World joint | Degrees of freedom |
|---|---|---|
| `UsdPhysics.RevoluteJoint` | revolute | 1 rotational, with limits |
| `UsdPhysics.PrismaticJoint` | prismatic | 1 translational, with limits |
| `UsdPhysics.SphericalJoint` | spherical | 3 rotational |
| `UsdPhysics.FixedJoint` | fixed | 0 (rigid link-to-link weld) |
| `UsdPhysics.Joint` (generic) | free | 6 (full translation + rotation) |

A joint's root link is *fixed* or *floating* according to the asset. Override this with `fixed` on the morph, which applies only to root (base) links:

```python
gs.morphs.USD(file="robot.usd", fixed=True)  # weld the base to the world
```

`examples/usd/kitchen.py` uses `fixed=False` so authored-fixed appliances such as the dishwasher become free bodies that drop onto the ground and can be dragged, and `fixed=None` to keep the scene's authored fixed/free states.

## Axis and units

USD stages carry their own `upAxis` and `metersPerUnit` metadata, and Genesis World honors it when transforming the asset into its right-handed, Z-up, meters world. When a referenced mesh omits that information, the `file_meshes_are_zup` morph option controls interpretation the same way it does for other mesh formats. See {doc}`conventions` for the full axis- and unit-handling rules, including the Blender-aligned Y-up ↔ Z-up mapping Genesis World follows.

## Mesh processing

Collision meshes are derived from the asset's geometry. Three options control that derivation; `examples/usd/kitchen.py` sets all three to honor the asset as authored:

```python
scene.add_stage(
    morph=gs.morphs.USD(
        file=usd_file,
        fixed=fixed,
        convexify=False,  # Don't force convex hulls; honor the asset's per-geom MeshCollisionAPI approximation.
        decimate=True,  # Simplify collision meshes (fewer faces) for speed and stability.
        align=False,  # Keep the USD root-link frames (don't re-center to the center of mass).
    ),
    vis_mode="visual",  # Render the asset's own USD materials, not the per-collision debug colors.
)
```

- **`convexify`** wraps each mesh in one or more convex hulls (decomposing with `coacd` when a single hull is too coarse). It defaults to `True` for rigid entities. Set it to `False` to keep concave collision geometry the asset already provides.
- **`decimate`** simplifies collision meshes toward `decimate_face_num` (default 500) faces. It defaults to `True` when `convexify` is on.
- **`align`** re-frames floating-base root links so the origin sits at the center of mass. It defaults to `False`.

`vis_mode="collision"` renders the collision geometry instead of the visual meshes, which is the fastest way to check that collision shapes match what you expect.

## Joint dynamics attributes

Some joint properties (friction, armature, passive stiffness and damping) are not part of the core USD physics schema, so exporters store them under custom attribute names. Isaac Sim, for example, writes `physxJoint:jointFriction` and `physxLimit:angular:stiffness`. Genesis World reads each property from a list of candidate attribute names, trying them in order and using the first that exists:

```python
gs.morphs.USD(
    file="robot.usd",
    joint_friction_attr_candidates=[
        "physxJoint:jointFriction",  # Isaac Sim
        "physics:jointFriction",
        "jointFriction",
        "friction",
    ],
)
```

The defaults already cover Isaac Sim and common community conventions; override a candidate list only when your exporter uses a name none of them match. The parsed values populate the corresponding `dof` fields:

| Morph option | `dof` field it fills | Meaning |
|---|---|---|
| `joint_friction_attr_candidates` | `dofs_frictionloss` | passive joint friction |
| `joint_armature_attr_candidates` | `dofs_armature` | reflected rotor inertia |
| `revolute_joint_stiffness_attr_candidates` | `dofs_stiffness` | passive stiffness (revolute) |
| `revolute_joint_damping_attr_candidates` | `dofs_damping` | passive damping (revolute) |
| `prismatic_joint_stiffness_attr_candidates` | `dofs_stiffness` | passive stiffness (prismatic) |
| `prismatic_joint_damping_attr_candidates` | `dofs_damping` | passive damping (prismatic) |

PD control gains authored through the USD `PhysicsDriveAPI` (`physics:stiffness`, `physics:angular:damping`) are read into `dofs_kp` and `dofs_kv` directly, since those are standard USD attributes.

## Separating visual and collision geometry

When an asset does not declare collision geometry through `MeshCollisionAPI`, Genesis World infers it from prim names. It matches each prim against regex patterns and inherits the match down the subtree:

```python
gs.morphs.USD(
    file="robot.usd",
    collision_mesh_prim_patterns=[r"^([cC]ollision).*"],  # collision-only geometry
    visual_mesh_prim_patterns=[r"^([vV]isual).*"],  # visual-only geometry
)
```

The rules, in order of application:

1. **Inheritance.** The parser traverses the prim hierarchy top-down. Once a prim matches a pattern, every descendant inherits that classification.
2. **Classification.** A prim matching only the visual pattern is visual-only; one matching only the collision pattern is collision-only; one matching both, or neither, is used for both. The neither case is the default for mesh-only assets that carry no naming convention.
3. **Visibility and purpose.** Only visible prims are parsed. Prims with `purpose = "guide"` are excluded from visuals but may still serve as collision geometry.

The patterns above are the defaults, so most Isaac Sim assets need no configuration here.

(material-baking)=
## Material baking

`usd-core` parses `UsdPreviewSurface` materials, which covers most assets. Materials built on other shader networks require NVIDIA Omniverse Kit to bake them into a supported form. Baking is available on Python 3.10 and 3.11 with a GPU backend:

```bash
pip install --extra-index-url https://pypi.nvidia.com/ omniverse-kit
export OMNI_KIT_ACCEPT_EULA=yes
```

`OMNI_KIT_ACCEPT_EULA=yes` accepts the Omniverse EULA non-interactively; set it once. Without Omniverse Kit, Genesis World parses only `UsdPreviewSurface` and falls back to each prim's `displayColor` where no material is present.

:::{note}
If you see a `Baking process failed: ...` warning, the usual causes are an unaccepted EULA (set `OMNI_KIT_ACCEPT_EULA=yes`), a first-launch dependency install that timed out (rerun the program once it finishes), or stale extensions across multiple Python environments (remove the shared extension folder, e.g. `~/.local/share/ov/data/ext` on Linux, and retry).
:::

## See also

- {doc}`conventions`: coordinate frame, units, and Y-up ↔ Z-up handling.
- {doc}`control_your_robot` and {doc}`inverse_kinematics_motion_planning`: actuating and planning for a USD-loaded articulation.
- {doc}`parallel_simulation`: running USD assets across many environments on the GPU.
- {doc}`/api_reference/options/morph/index`: the full `gs.morphs` reference, including every `USD` option.
