# Camera sensors

A camera sensor renders the scene to an RGB image off-screen and returns it through the sensor pipeline. Add one with `scene.add_sensor(...)`, step the simulation, and call `read()` to get pixels back as a tensor. No viewer window required.

A camera sensor is distinct from two things it is easy to confuse it with:

- The **viewer** (`show_viewer=True`) is the interactive window a human watches. It renders live and returns nothing to your code. See {doc}`/user_guide/interaction/visualization`.
- The **visualization camera** (`scene.add_camera().render(...)`) renders color, depth, segmentation, and surface-normal images on demand. Use it when you want the four image channels. It is covered in {doc}`/user_guide/rendering/rendering`.

A camera sensor, by contrast, is a first-class {doc}`sensor <index>`: it renders lazily on `read()`, participates in the batched `scene.read_sensors()` path, and can be attached to a moving link like any other sensor. It returns **RGB only**.

The complete script is [`examples/sensors/camera_as_sensor.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/camera_as_sensor.py).

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(show_viewer=False)
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Sphere(radius=0.5, pos=(0.0, 0.0, 2.0)))

camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(500, 600),        # (width, height), pixels
        pos=(3.0, 0.0, 2.0),   # world frame when unattached, meters
        lookat=(0.0, 0.0, 1.0),
        fov=60.0,              # vertical field of view, degrees
    ),
)

scene.build()
scene.step()

data = camera.read()
print(data.rgb.shape)  # (600, 500, 3) — (H, W, 3), H and W from res=(W, H)
```

`add_sensor` returns the sensor object; interact with the camera through it rather than a global handle. The default renderer is the rasterizer, so this runs on any platform without extra setup.

## What `read()` returns

`read()` renders the current scene state if it is stale, then returns a `CameraReturnType`, a `NamedTuple` whose single field is the color image:

```python
data = camera.read()
rgb = data.rgb  # shape ([n_envs,] H, W, 3), dtype uint8, values 0–255
```

The image is `(H, W, 3)` with `H = res[1]` and `W = res[0]`. Note that `res` is `(width, height)` but the array is row-major `(height, width)`, matching NumPy image conventions. The leading `n_envs` axis is present only when the scene is built with environments (`scene.build(n_envs=...)`); an unbatched `scene.build()` drops it.

Pass `envs_idx` to read a subset of environments:

```python
data = camera.read(envs_idx=[0, 2])
print(data.rgb.shape)  # (2, H, W, 3)
```

The example saves each frame with matplotlib; `read()` returns a GPU tensor, so convert it first:

```python
from genesis.utils.misc import tensor_to_array

data = camera.read()
rgb = data.rgb[0] if data.rgb.ndim > 3 else data.rgb  # drop the env axis if present
plt.imsave("frame.png", tensor_to_array(rgb))
```

## Rendering backends

Three backends render RGB. They share the common options below and differ in speed, fidelity, and platform support:

| Options class | Backend | Environments | Best for |
|---|---|---|---|
| `RasterizerCameraOptions` | OpenGL | sequential | fast real-time rendering on any platform |
| `RaytracerCameraOptions` | LuisaRender | single environment | photo-realistic offline renders |
| `BatchRendererCameraOptions` | Madrona (GPU) | parallel | high-throughput RL training (CUDA only) |

Select a backend by choosing the matching options class; no separate scene `renderer` argument is required for the rasterizer. For photo-realistic path tracing, prefer the Nyx renderer described in {doc}`/user_guide/rendering/nyx_renderer`.

Common parameters (all backends):

```python
gs.sensors.RasterizerCameraOptions(
    res=(512, 512),        # (width, height), pixels
    pos=(3.5, 0.0, 1.5),   # camera position; link-relative when attached
    lookat=(0.0, 0.0, 0.0),
    up=(0.0, 0.0, 1.0),
    fov=60.0,              # vertical field of view, degrees
    lights=[],             # per-camera lights, backend-specific dicts
)
```

Backend-specific options include `near` / `far` clipping planes (rasterizer and batch renderer, meters), `model` / `spp` / `denoise` and thin-lens depth-of-field controls (ray tracer), and `use_rasterizer` (batch renderer). See the options classes in [`genesis/options/sensors/camera.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/genesis/options/sensors/camera.py) for the full list and defaults.

## Attaching a camera to a link

Set `entity_idx` (and optionally `link_idx_local`) to mount the camera on an entity. The camera then follows that link's motion each step, so `read()` always renders from the current pose:

```python
camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(500, 600),
        pos=(0.0, 0.0, 1.0),        # relative to the link frame once attached
        lookat=(0.0, 0.0, 0.0),
        fov=70.0,
        entity_idx=robot.idx,       # -1 or None for a static, world-fixed camera
        link_idx_local=0,           # which link of the entity to mount on
    ),
)
```

For a fixed mounting transform relative to the link, pass `offset_T`, a 4×4 homogeneous matrix. When given, it takes priority over `pos_offset` / `euler_offset`:

```python
import numpy as np

gs.sensors.RasterizerCameraOptions(
    # ... res, fov, entity_idx, link_idx_local as above ...
    offset_T=np.eye(4),  # camera pose relative to the attached link
)
```

## Multiple environments

Build with `n_envs` to render every environment in one pass. The batch renderer runs them in parallel on the GPU; the rasterizer renders them sequentially:

```python
scene.build(n_envs=4)
scene.step()

data = camera.read()
print(data.rgb.shape)  # (4, H, W, 3)
```

:::{note}
All `BatchRendererCameraOptions` cameras in a scene must share the same resolution.
:::

## Notes and gotchas

:::{note}
**Camera sensors return RGB only.** `read()` gives you the color image and nothing else. For depth, segmentation masks, or surface normals, use the visualization camera's `render()` method (see {doc}`/user_guide/rendering/rendering`) or, for depth specifically, the {doc}`depth-camera raycaster sensor <raycaster>`.
:::

:::{warning}
Camera sensors do not support `history_length`. They render lazily on `read()` and bypass the shared sensor cache that backs the history buffer, so setting it raises an error at construction. Read once per step instead.
:::

## See also

- {doc}`/user_guide/rendering/rendering`: the visualization camera's four image channels, video recording, and rendering backends.
- {doc}`Sensors <index>`: the sensor pipeline, batched reads, and other sensor families.
- {doc}`Raycaster sensors <raycaster>`: depth camera and lidar with configurable ray patterns.
