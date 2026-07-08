# Camera sensor

A camera sensor renders an RGB image of the scene each step and returns it through the sensor `read()` interface, so a camera reads like any other sensor: attach it, step, read.

Do not confuse it with the visualization camera. The camera sensor is created with `scene.add_sensor(gs.sensors.*CameraOptions(...))` and its `read()` returns a `CameraReturnType` carrying a single `rgb` field. The visualization camera is created with `scene.add_camera(...)` and its `render()` returns RGB together with depth, segmentation, and surface normals. Reach for the visualization camera when you need those extra channels or the interactive viewer; see {doc}`/api_reference/visualization/cameras/index`.

## Minimal example

```python
import genesis as gs

gs.init(backend=gs.gpu)
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.URDF(file="urdf/go2/urdf/go2.urdf"))

camera = scene.add_sensor(
    gs.sensors.RasterizerCameraOptions(
        res=(640, 480),      # (width, height)
        pos=(3.5, 0.0, 1.5),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,            # vertical field of view, degrees
    )
)

scene.build()
scene.step()

frame = camera.read()  # CameraReturnType
rgb = frame.rgb        # uint8, shape ([n_envs,] height, width, 3)
```

`read()` renders lazily: the first call after a step renders the current state, and repeated calls within the same step reuse the cached image. Attach the camera to a link by passing `entity_idx` and `link_idx_local`, exactly as for other sensors; `pos`, `lookat`, and `up` are then interpreted relative to the link frame.

## Choosing a backend

Each backend is a separate options class and sensor. All three return the same `CameraReturnType(rgb)`; they differ in the renderer they drive and the hardware they require.

| `gs.sensors.*` | Renderer | Multiple environments | Requires |
|---|---|---|---|
| `RasterizerCameraOptions` | OpenGL rasterizer | Supported (set `env_separate_rigid=True` in `VisOptions`) | OpenGL |
| `RaytracerCameraOptions` | LuisaRender path tracer | Not supported (`n_envs > 1` raises) | Scene built with `renderer=gs.renderers.RayTracer(...)` |
| `BatchRendererCameraOptions` | Madrona batch renderer | Supported, batched on GPU | CUDA backend |

Use the rasterizer for fast RGB with no special setup. Use the raytracer for photorealistic single-environment renders. Use the batch renderer when rendering many parallel environments on a GPU.

## Rasterizer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.RasterizerCameraOptions
   :members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.camera.RasterizerCameraSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## Raytracer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.RaytracerCameraOptions
   :members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.camera.RaytracerCameraSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## Batch renderer camera

```{eval-rst}
.. autoclass:: genesis.options.sensors.camera.BatchRendererCameraOptions
   :members:
   :show-inheritance:

.. autoclass:: genesis.engine.sensors.camera.BatchRendererCameraSensor
   :members:
   :undoc-members:
   :show-inheritance:
```

## See also

- {doc}`index`: sensor overview and return-shape table.
- {doc}`/api_reference/visualization/cameras/index`: the visualization camera (`scene.add_camera().render()`) for depth, segmentation, and normals.
