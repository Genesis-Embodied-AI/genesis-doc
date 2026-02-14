# Rasterizer

`Rasterizer` 使用 OpenGL 提供快速的 GPU 加速渲染。它是实时可视化的默认渲染器，适用于训练强化学习智能体。

## 概述

Rasterizer 提供：

- **高性能**：简单场景下可达 1000+ FPS
- **GPU 加速**：利用 OpenGL 进行渲染
- **多种输出**：RGB、深度、分割、法线
- **多环境支持**：高效的批处理渲染

## 快速开始

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# 添加实体
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.URDF(file="path/to/robot.urdf"))

scene.build()

# 添加 rasterizer 相机（默认）
cam = scene.add_camera(
    res=(640, 480),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
)

# 渲染图像
for i in range(100):
    scene.step()

    rgb = cam.render(rgb=True)
    depth = cam.render(depth=True)
    segmentation = cam.render(segmentation=True)
```

## 配置

通过 `RasterizerOptions` 配置 Rasterizer：

```python
rasterizer_options = gs.options.RasterizerOptions(
    env_separate_rigid=True,   # 每个环境单独渲染
)
```

## 输出类型

| 输出 | 类型 | 描述 |
|--------|------|-------------|
| `rgb` | `np.ndarray` (H, W, 3) | RGB 彩色图像 |
| `depth` | `np.ndarray` (H, W) | 以米为单位的深度值 |
| `segmentation` | `np.ndarray` (H, W) | 实体/连杆分割 ID |
| `normal` | `np.ndarray` (H, W, 3) | 表面法线 |

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.rasterizer.Rasterizer
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`raytracer` - 照片级真实感光线追踪渲染器
- {doc}`batch_renderer` - 高吞吐量并行渲染器
- {doc}`/api_reference/options/renderer/rasterizer` - Rasterizer 选项
