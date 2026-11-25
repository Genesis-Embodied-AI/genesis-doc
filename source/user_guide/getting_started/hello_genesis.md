# Hello, Genesis World

This tutorial builds the smallest complete Genesis World program. It loads a Franka arm above a ground plane and lets the arm fall under gravity. The program is under fifteen lines. It contains every step that any Genesis World simulation needs:

- Initialize

- Create a scene

- Add entities

- Build and step

Each step is explained in detail below for building the Genesis World simulation.

```{figure} ../../_static/images/hello_genesis.png
:alt: A Franka arm resting on the ground plane in the Genesis World viewer
```

## Script for building the Genesis World program

The complete script to build is [`examples/tutorials/hello_genesis.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/hello_genesis.py):

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene()

plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)

scene.build()
for i in range(1000):
    scene.step()
```

## Initialize

`gs.init()` must run once before you touch any other part of the API. Its most important argument is the compute **backend**:

```python
gs.init(backend=gs.cpu)
```

- **Backend.** `gs.cpu` runs anywhere. For GPU-accelerated {doc}`parallel simulation <parallel_simulation>`, use `gs.cuda`, `gs.amdgpu`, or `gs.metal`. `gs.gpu` selects the GPU backend your machine has: CUDA on NVIDIA, ROCm on AMD, or Metal on Apple Silicon.
- **Precision.** Genesis World uses 32-bit floats by default. For double precision, pass `precision="64"`.
- **Logging.** On init, Genesis World logs system and version information. Set `logging_level="warning"` to quiet it, and `theme="light"` for light-background terminals.
- **Performance mode.** With `performance_mode=True`, Genesis World bakes static tensor shapes into its compiled kernels, allowing simulation runs roughly 30% faster; however, with every change to the scene triggers a recompile that takes several minutes. Leave it off for research, debugging, and interactive work. Turn it on for policy training and production runs.

For the full set of `gs.init()` arguments (backend selection and fallback, precision, seeding and determinism, logging, and environment variables), see {doc}`Initialization and backends </user_guide/configuration/initialization>`.

## Create a scene

Every object, robot, camera, and light belongs in a scene (see the {doc}`Scene API </api_reference/engine/scene>`). A scene owns two parts:

- `simulator`: the physics solvers.

-  `visualizer`: everything you see.

```python
scene = gs.Scene()
```

The default scene is headless. To open the interactive wnindow, pass `show_viewer=True`. Use the options objects to configure physics and the camera:

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, gravity=(0, 0, -10.0)),
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    show_viewer=True,
)
```

Here `dt` is the simulation timestep in seconds, `gravity` points down along `-Z` axis, and the viewer options set the initial camera pose.

## Add entities

Objects and robots are {doc}`entities </api_reference/engine/entity/index>`. The API is object-oriented: `add_entity` returns the entity itself and you control it through its own methods and attributes.

The first argument to `add_entity` is a {doc}`morph </api_reference/engine/entity/morph/index>`. Morph is a combined description of an entity's geometry and initial pose. Build a morph from a shape primitive, or load one from a file:

```python
plane = scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(
    gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"),
)
```

Shape primitives include `Plane`, `Box`, `Cylinder`, and `Sphere`. `Terrain` builds a height-field ground (see the {doc}`terrain tutorial </user_guide/physics/terrain>`), and `Drone` loads a quadrotor from a URDF file. 

Genesis World supports these file formats:

- {py:class}`gs.morphs.MJCF <genesis.options.morphs.MJCF>`: MuJoCo `.xml` models
- {py:class}`gs.morphs.URDF <genesis.options.morphs.URDF>`: robot descriptions (`.urdf`, and `.xacro`, which is preprocessed automatically)
- {py:class}`gs.morphs.USD <genesis.options.morphs.USD>`: Universal Scene Description (`.usd`, `.usda`, `.usdc`, `.usdz`); see the {doc}`USD import tutorial </user_guide/assets/usd_import>`
- {py:class}`gs.morphs.Mesh <genesis.options.morphs.Mesh>`: non-articulated meshes (`.obj`, `.stl`, `.glb`, `.gltf`); see {doc}`Conventions </user_guide/configuration/conventions>` for Y-up vs. Z-up handling

A morph also accepts pose and scale. Orientation is either `euler` (SciPy extrinsic x-y-z, in degrees) or `quat` (`(w, x, y, z)`):

```python
franka = scene.add_entity(
    gs.morphs.MJCF(
        file="xml/franka_emika_panda/panda.xml",
        pos=(0, 0, 0),
        euler=(0, 0, 90),
        scale=1.0,
    ),
)
```

File paths can be absolute or relative. Genesis World resolves a relative path against your working directory *and* against the bundled asset directory (`genesis/assets`). For example, `xml/franka_emika_panda/panda.xml` loads the Franka model that ships with Genesis World.

:::{note}
An MJCF file specifies the joint connecting the robot's base to the world. A URDF does not. A URDF base is free (a 6-dof joint to the world) unless you pass `fixed=True`. The same applies to `gs.morphs.Mesh`.
:::

## Build and step

```python
scene.build()
for i in range(1000):
    scene.step()
```

You must call `scene.build()` explicitly. Genesis World compiles GPU kernels just-in-time. Building allocates device memory, creates the simulation data fields, and triggers that compilation. With `show_viewer=True`, the viewer window opens once the scene is built.

Each `scene.step()` then advances the simulation by one `dt`. When the viewer is shown, stepping run in real time by default. To run as fast as possible, pass `gs.options.ViewerOptions(realtime_factor=None)`.

:::{note}
**Kernel compilation and caching.** The first build with a new scene configuration compiles kernels on the fly, which is slow. A new configuration is anything that changes the internal data layout, such as different robots or a different number of objects. Genesis World caches the compiled kernels. If the first run exits normally or with Ctrl-C (not Ctrl-\), later runs with the same configuration load from the cache and start quickly.
:::

## Next steps

- {doc}`Control your robot <control_your_robot>`: actuate the Franka you just loaded.
- {doc}`Visualization </user_guide/interaction/visualization>`: watch a scene in the interactive viewer.
- {doc}`Rendering </user_guide/rendering/cameras>`: capture images and video from a camera.
