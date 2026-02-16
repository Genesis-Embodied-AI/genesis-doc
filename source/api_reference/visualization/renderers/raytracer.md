# Raytracer

`Raytracer` 使用路径追踪提供照片级真实感渲染。它专为生成高质量图像和视频而设计。

## 概述

Raytracer 提供：

- **照片级真实感质量**：全局照明、反射、折射
- **物理准确性**：正确的光传输仿真
- **高级材质**：PBR 材质、次表面散射
- **降噪**：基于 AI 的降噪以加速收敛

## 快速开始

```python
import genesis as gs

gs.init()
scene = gs.Scene()

# 添加带材质的实体
plane = scene.add_entity(
    gs.morphs.Plane(),
    surface=gs.surfaces.Plastic(),
)
box = scene.add_entity(
    gs.morphs.Box(pos=(0, 0, 0.5)),
    surface=gs.surfaces.Metal.Gold(),
)

scene.build()

# 添加 raytracer 相机
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    fov=40,
    spp=256,        # 每像素采样数
    denoise=True,   # 启用降噪
)

# 渲染高质量图像
scene.step()
rgb = cam.render(rgb=True)
```

## 配置

Raytracer 相机的关键参数：

| 参数 | 描述 | 默认值 |
|-----------|-------------|---------|
| `spp` | 每像素采样数（越高 = 噪点越少） | 256 |
| `denoise` | 启用 AI 降噪 | False |
| `model` | 相机模型（`pinhole` 或 `thinlens`） | `pinhole` |
| `aperture` | 景深光圈 | 0.0 |
| `focus_dist` | 对焦距离 | 自动 |

## Thin Lens（景深）

```python
cam = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 0, 2),
    lookat=(0, 0, 0.5),
    model="thinlens",
    aperture=0.1,      # 越大 = 越模糊
    focus_dist=3.0,    # 到焦平面的距离
    spp=512,
)
```

## 光线追踪材质

Raytracer 支持高级表面材质：

- **Plastic**：带可选粗糙度的漫反射
- **Metal**：反射性金属表面（金、铜、铁等）
- **Glass**：透明/折射材质
- **Emission**：发光表面

查看 {doc}`/api_reference/options/surface/index` 了解所有表面类型。

## API 参考

```{eval-rst}
.. autoclass:: genesis.vis.raytracer.Raytracer
   :members:
   :undoc-members:
   :show-inheritance:
```

## 另请参阅

- {doc}`rasterizer` - 快速光栅化渲染器
- {doc}`/api_reference/options/surface/index` - 表面材质
- {doc}`/api_reference/options/renderer/raytracer` - Raytracer 选项
