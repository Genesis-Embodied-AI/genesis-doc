# Visualization and rendering

This tutorial covers how to see a Genesis World scene: the interactive viewer for watching a simulation live, and camera sensors for rendering images off-screen. You will add a camera, render color, depth, segmentation, and surface-normal images, and record a video.

Every scene owns a `visualizer` (`scene.visualizer`) that drives both paths. There are two ways to look at a scene:

- **The viewer** is an interactive window that runs in its own thread and follows the simulation in real time. Use it while developing on a machine with a display.
- **Camera sensors** render frames on demand and return them as arrays. They are not tied to the viewer or a display, so they work headless: on a render farm, in a container, or over SSH.

The complete script is [`examples/tutorials/visualization.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/visualization.py).

## The viewer

Configure the scene's visuals through two options objects. `viewer_options` controls the interactive window; `vis_options` controls visual properties shared by the viewer *and* every camera (frame gizmos, lighting, reflections). Pass `show_viewer=True` to open the window:

```python
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        res=(1280, 960),
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,  # draw the world coordinate frame at the origin
        world_frame_size=1.0,  # length of each axis, in meters
        show_link_frame=False,  # do not draw per-link frames
        show_cameras=False,  # do not draw camera meshes and frustums
        plane_reflection=True,
        ambient_light=(0.1, 0.1, 0.1),
    ),
    renderer=gs.renderers.Rasterizer(),
    show_viewer=True,
)
```

`camera_pos` and `camera_lookat` are in meters, in the right-handed, Z-up world frame. `camera_fov` is the vertical field of view in degrees. If `res` is `None`, Genesis World opens a 4:3 window sized to half your display height.

The viewer always renders with the rasterizer; `renderer` selects the backend used by camera sensors (see [Rendering backends](#rendering-backends)).

:::{note}
To cap the viewer frame rate, set `refresh_rate` on `ViewerOptions`. The older `max_FPS` argument is deprecated and now maps to `refresh_rate`.
:::

Once the scene exists, reach the viewer through the `scene.viewer` shortcut to read or set the camera pose at runtime:

```python
pose = scene.viewer.camera_pose
scene.viewer.set_camera_pose(pos=(3.5, 0.0, 2.5), lookat=(0, 0, 0.5))
```

## Command-line tools

Installing Genesis World adds a `gs` command with a few subcommands, so you can open the viewer without writing a script. Run `gs` with no arguments to list them.

**`gs launch [asset]`** opens an asset in the interactive viewer. It accepts a Mesh, URDF, MJCF, or USD file; for a USD stage, every rigid entity in the stage is loaded. The viewer's overlay exposes per-joint sliders and play, pause, step, and reset controls, and it starts paused so you can inspect and pose the asset first. With no file, it opens an empty scene to which you can add entities live. Useful flags: `-c` visualize collision geometry, `-r` slowly rotate the asset, `-s SCALE` scale it, and `-l` show link frames.

```bash
gs launch xml/franka_emika_panda/panda.xml
```

**`gs play [asset]`** opens the same interactive viewer but runs the physics simulation, so joints and bodies respond under gravity and contact. With no file, it loads a demo scene (a Franka arm on a ground plane). It accepts `-c` and `-s SCALE`.

```bash
gs play xml/franka_emika_panda/panda.xml
```

**`gs animate 'pattern'`** combines every image matching a glob pattern into a video written to `video.mp4`. Pass `--fps` to set the frame rate (default 30).

```bash
gs animate 'frames/*.png' --fps 60
```

:::{note}
`gs view` still works as a deprecated alias of `gs launch` and prints a deprecation warning. Use `gs launch` instead.
:::

## Lighting

The rasterizer (the viewer and any rasterizer camera sensor) lights the scene from a list of lights on `VisOptions`. With no configuration it uses a single directional light, so scenes are lit out of the box; set `lights` to control direction, color, and intensity yourself. The light classes live in `gs.options.vis`:

```python
scene = gs.Scene(
    vis_options=gs.options.VisOptions(
        lights=[
            gs.options.vis.DirectionalLight(
                dir=(-1, -1, -1),  # direction the light travels, world frame
                color=(1.0, 1.0, 1.0),  # RGB in [0, 1]
                intensity=5.0,
            ),
            gs.options.vis.PointLight(
                pos=(2.0, 0.0, 3.0),  # meters, world frame
                color=(1.0, 0.9, 0.8),
                intensity=8.0,
            ),
        ],
        ambient_light=(0.1, 0.1, 0.1),  # uniform fill so shadows are not pure black
    ),
)
```

Two light types are available:

- **`DirectionalLight`:** parallel rays from a fixed direction, like sunlight. Set `dir` (the direction the light travels), `color`, and `intensity`. Position does not matter.
- **`PointLight`:** light radiating outward from a point. Set `pos`, `color`, and `intensity`.

Ambient light is a separate, uniform fill set through the `ambient_light` field rather than an entry in `lights`.

:::{note}
This controls the rasterizer only. The ray tracer has no light objects: lights there are entities with an `Emission` surface, covered in {doc}`Surfaces and textures <surfaces_textures>`. The `BatchRenderer` backend instead takes lights at runtime through `scene.add_light(...)`.
:::

## Adding a camera

A camera is a sensor you add to the scene. It renders independently of the viewer, so it is the tool for headless rendering and for capturing views from angles other than the viewer's:

```python
cam = scene.add_camera(
    res=(640, 480),  # (width, height) in pixels
    pos=(3.5, 0.0, 2.5),
    lookat=(0, 0, 0.5),
    fov=30,
    GUI=False,
)
```

With `GUI=True`, the camera opens an OpenCV window that displays each rendered frame. This is separate from the viewer window. Leave it `False` when running headless.

## Rendering images

Build the scene, then call `cam.render()`. The camera can produce four image types: color, depth, segmentation mask, and surface normals. Only RGB is rendered by default; enable the others with keyword flags. `render()` always returns the four in the same order, with disabled types returned as `None`:

```python
scene.build()

# render rgb, depth, segmentation, normal
rgb, depth, segmentation, normal = cam.render(rgb=True, depth=True, segmentation=True, normal=True)
```

Each returned array is shaped `(height, width, ...)` following the `res=(width, height)` you set. By default the segmentation mask stores an integer object index per pixel; set `colorize_seg=True` for a viewable color mask. The index maps back to scene objects at the level set by `VisOptions.segmentation_level` (for example, `link_idx` into `scene.rigid_solver.links`).

```{figure} ../../_static/images/multimodal.png
:alt: The Franka scene rendered four ways: color, depth, segmentation mask, and surface normals
```

:::{tip}
OpenCV windows opened with `GUI=True` sometimes render black on the first frame. Call `cam.render()` again to refresh them, or `cv2.waitKey(1)`.
:::

## Recording a video

To capture a video, call `start_recording()`, render a frame each step, then `stop_recording()` to encode the accumulated frames. Every `cam.render()` call between the two is added to the recording. Here the camera orbits the scene while the simulation steps:

```python
import math

cam.start_recording()

for i in range(120):
    scene.step()
    cam.set_pose(
        pos=(3.0 * math.sin(i / 60), 3.0 * math.cos(i / 60), 2.5),
        lookat=(0, 0, 0.5),
    )
    cam.render()

cam.stop_recording(save_to_filename="video.mp4", fps=60)
```

If you omit `save_to_filename`, Genesis World generates a name from the calling script. The result:

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/cam_record.mp4" type="video/mp4">
</video>

## Rendering backends

`gs.Scene(renderer=...)` selects how camera sensors turn the scene into pixels. Genesis World provides:

- `gs.renderers.Rasterizer()`: the default. Fast, and what the viewer always uses.
- `gs.renderers.RayTracer()`: a path tracer for photorealistic stills (see [below](#photorealistic-rendering-with-luisa-deprecating)).
- `gs.renderers.BatchRenderer(...)`: high-throughput rendering across many environments (see [Batch rendering with gs-madrona](#batch-rendering-with-gs-madrona)).

**Nyx** is the recommended path toward photorealistic rendering. Unlike the backends above, it attaches as a camera *sensor* rather than a scene-wide renderer.

(photo-realistic-rendering-with-nyx)=
### Photorealistic rendering with Nyx

[Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx) is a GPU-accelerated path tracer purpose-built for Genesis World. It is wired in as a **camera sensor**: you attach a `NyxCameraOptions` sensor to the scene and read frames back from `cam.read().rgb`. It supports PBR materials, HDRI lighting, 3D Gaussian splat assets, attached and multi-camera setups, multi-environment rendering, and per-pixel object picking.

#### Installation

Nyx ships as the `gs-nyx` package:

```bash
pip install gs-nyx
```

:::{note}
`gs-nyx` is currently distributed through an internal package index while the project is being prepared for public release. Public installation instructions will be published at the [Nyx repository](https://github.com/Genesis-Embodied-AI/genesis-nyx) once the wheel is on PyPI.
:::

Verify the install by importing the plugin alongside Genesis World:

```python
import genesis as gs
import gs_nyx.nyx_py_renderer as npr
import gs_nyx.nyx_py_sdk as nps
from gs_nyx_plugin.nyx_camera_options import NyxCameraOptions
```

#### A minimal example

The snippet below renders a PBR ball on a plane lit purely by an HDRI environment map, the canonical "hello world" for Nyx, mirroring [`examples/01_hello_nyx.py`](https://github.com/Genesis-Embodied-AI/genesis-nyx/blob/main/examples/01_hello_nyx.py) in the Nyx repo.

```{image} ../../_static/images/nyx_hello.png
:alt: PBR ball rendered with Nyx under an HDRI environment map
:align: center
:width: 80%
```

```python
import os
from PIL import Image

import genesis as gs
import gs_nyx.nyx_py_renderer as npr
import gs_nyx.nyx_py_sdk as nps
from gs_nyx_plugin.nyx_camera_options import NyxCameraOptions


HERE = os.path.dirname(__file__)
PBR_BALL = os.path.join(HERE, "assets", "PBR_Ball.glb")
ENV_MAP = os.path.join(HERE, "assets", "kloppenheim_07_puresky_4k.hdr")
OUTPUT_PATH = os.path.join(HERE, "out", "01_hello_nyx.png")


def main():
    gs.init()

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01),
        show_viewer=False,
    )

    scene.add_entity(morph=gs.morphs.Plane(plane_size=(10.0, 10.0)))
    scene.add_entity(
        morph=gs.morphs.Mesh(file=PBR_BALL, pos=(0.0, 0.0, 0.0)),
        surface=gs.surfaces.Gold(),
    )

    # describe how the env map is encoded
    env_map = nps.EnvironmentMapAsset()
    env_map.texture = ENV_MAP
    env_map.layout = nps.EEnvMapLayout.LongLat
    env_map.multiplier = 8

    # attach a Nyx camera sensor
    cam = scene.add_sensor(
        NyxCameraOptions(
            res=(1920, 1080),
            pos=(-1.0, 1.0, 1.2),
            lookat=(0.0, 0.0, 0.1),
            fov=20.0,
            spp=64,
            render_mode=npr.ERenderMode.FastPathTracer,
            env_maps=(env_map,),
        )
    )

    scene.build(n_envs=1)
    scene.step()  # rendering happens during the sim step

    rgb = cam.read().rgb[0].cpu().numpy()
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    Image.fromarray(rgb).save(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

Three things distinguish Nyx from the other backends:

- **Nyx is a sensor.** Register it with `scene.add_sensor(NyxCameraOptions(...))`, not as the scene `renderer`.
- **Rendering happens during `scene.step()`.** Read frames back via `cam.read().rgb`, a torch tensor with one image per environment.
- **`spp`** (samples per pixel) and **`render_mode`** trade quality for speed; `FastPathTracer` is a good default for iteration.

For advanced features such as Gaussian splats, multi-camera setups, and object picking, see the {doc}`Nyx renderer <nyx_renderer>` page and the [Nyx documentation site](https://genesis-embodied-ai.github.io/genesis-nyx/).

:::{note}
**Roadmap.** We are unifying rasterization and path tracing under Nyx as a single, sensor-based rendering interface. Nyx will gradually replace both the Luisa backend below and the default rasterizer. Over time, all camera-based rendering in Genesis World will go through Nyx.
:::

### Photorealistic rendering with Luisa (deprecating)

Genesis World also ships a Luisa-based ray-tracing backend. Enable it by passing `renderer=gs.renderers.RayTracer()` when creating the scene; it exposes extra parameters such as `spp`, `aperture`, and camera `model`.

:::{warning}
This backend is deprecated in favor of Nyx and requires building `LuisaRender` from source. Prefer Nyx for new work.
:::

Setup, tested on Ubuntu 22.04 with CUDA 12.4 and Python 3.9:

1. Fetch the submodule and install the render extras:

   ```bash
   # inside the genesis-world repo
   git submodule update --init --recursive
   pip install -e ".[render]"
   ```

2. Ensure `gcc`/`g++` >= 11 and CMake >= 3.26 are on your `PATH`, and install the Vulkan, X11, UUID, and zlib development headers (via `apt` with sudo, or `conda install -c conda-forge` without).

3. Build `LuisaRender`:

   ```bash
   cd genesis/ext/LuisaRender
   cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 \
       -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF \
       -D LUISA_RENDER_BUILD_TESTS=OFF
   cmake --build build -j $(nproc)
   ```

4. Run the demo:

   ```bash
   cd examples/rendering
   python demo.py
   ```

```{figure} ../../_static/images/raytracing_demo.png
:alt: A scene rendered photorealistically with the Luisa ray-tracing backend
```

:::{note}
Prebuilt LuisaRender binaries for common CUDA and Python combinations are available [on Google Drive](https://drive.google.com/drive/folders/1Ah580EIylJJ0v2vGOeSBU_b8zPDWESxS?usp=sharing), named `build_<commit-tag>_cuda<version>_python<version>`. Download the one matching your system, rename it to `build/`, and place it in `genesis/ext/LuisaRender`. For build and CUDA-toolkit troubleshooting, see the [genesis-world README](https://github.com/Genesis-Embodied-AI/genesis-world#quick-installation).
:::

### Batch rendering with gs-madrona

For high-throughput rendering across many parallel environments, use the gs-madrona backend by passing `renderer=gs.renderers.BatchRenderer(use_rasterizer=True)` (set `use_rasterizer=False` to path-trace instead).

Install the package first. Prebuilt wheels are available on PyPI for x86 and Python >= 3.10:

```bash
pip install gs-madrona
```

Then run the bundled example, which writes frames to `./image_output`:

```bash
python examples/rigid/single_franka_batch_render.py
```

## Next steps

Continue with {doc}`Control your robot <control_your_robot>` to actuate the Franka, or see {doc}`Sensors <sensors/index>` for reading data back from the scene. For the full photorealistic rendering reference, see the {doc}`Nyx renderer <nyx_renderer>` page.
