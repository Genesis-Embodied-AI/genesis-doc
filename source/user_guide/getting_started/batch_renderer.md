# 🎬 批量渲染器

BatchRenderer 使用 Madrona GPU 批量渲染技术，实现高吞吐量的多环境仿真。

## 安装

```bash
pip install gs-madrona
```

**要求：** Linux x86-64, NVIDIA CUDA, Python >= 3.10

## 基本设置

```python
import genesis as gs

gs.init(backend=gs.cuda)  # 需要 CUDA

scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(use_rasterizer=True),
)

plane = scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))

# 所有批量相机必须具有相同的分辨率
cam1 = scene.add_camera(res=(256, 256), pos=(2, 0, 1), lookat=(0, 0, 0.5))
cam2 = scene.add_camera(res=(256, 256), pos=(0, 2, 1), lookat=(0, 0, 0.5))

scene.build(n_envs=128)
```

## 渲染

```python
for step in range(1000):
    scene.step()

    # 渲染单个相机
    rgb, depth, seg, normal = cam1.render(
        rgb=True, depth=True, segmentation=True, normal=True
    )
    # 形状: (n_envs, H, W, C)

    # 或一次性渲染所有相机
    all_rgb = scene.render_all_cameras(rgb=True)
    # 形状: (n_cameras, n_envs, H, W, 3)
```

## 相机传感器 API

```python
camera = scene.add_sensor(
    gs.sensors.BatchRendererCameraOptions(
        res=(512, 512),
        pos=(3.0, 0.0, 2.0),
        lookat=(0.0, 0.0, 0.5),
        fov=60.0,
        near=0.1,
        far=100.0,
        lights=[{
            "pos": (2.0, 2.0, 5.0),
            "color": (1.0, 1.0, 1.0),
            "intensity": 1.0,
            "directional": True,
            "castshadow": True,
        }],
    )
)

scene.build(n_envs=64)

data = camera.read()  # 返回包含 .rgb tensor 的 CameraData
```

## 光照

```python
scene.add_light(
    pos=(0.0, 0.0, 3.0),
    dir=(0.0, 0.0, -1.0),
    color=(1.0, 1.0, 1.0),
    intensity=1.0,
    directional=True,
    castshadow=True,
)
```

## 分割

```python
scene = gs.Scene(
    renderer=gs.renderers.BatchRenderer(),
    vis_options=gs.options.VisOptions(
        segmentation_level="link",  # "entity", "link", 或 "geom"
    ),
)

# 渲染后
_, _, seg, _ = camera.render(segmentation=True)
colored = scene.visualizer.colorize_seg_idxc_arr(seg)
```

## 性能提示

- 所有相机使用相同的分辨率
- 推荐使用 `use_rasterizer=True` 以获得更高速度
- 使用 `scene.render_all_cameras()` 批量渲染所有相机
- 典型设置：256x256 分辨率，128-256 个环境
