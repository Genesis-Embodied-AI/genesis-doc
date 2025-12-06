# `gs.options.VisOptions`

`VisOptions` 是 Genesis API 中用于配置可视化和渲染选项的核心类，允许用户自定义场景的视觉呈现效果和交互行为。

## 主要功能

- 控制世界坐标系和链接坐标系的显示
- 配置阴影、反射和背景颜色等视觉效果
- 管理场景中的灯光设置
- 控制粒子的渲染方式和大小
- 支持物理边界的可视化
- 提供渲染质量和性能的调整选项

## 参数说明

| 参数名 | 类型 | 默认值 | 描述 |
|--------|------|--------|------|
| show_world_frame | `bool` | `False` | 是否显示世界坐标系 |
| world_frame_size | `float` | `1.0` | 世界坐标系的大小 |
| show_link_frame | `bool` | `False` | 是否显示链接坐标系 |
| link_frame_size | `float` | `0.2` | 链接坐标系的大小 |
| show_cameras | `bool` | `False` | 是否显示场景中的相机 |
| shadow | `bool` | `True` | 是否启用阴影效果 |
| plane_reflection | `bool` | `False` | 是否启用平面反射效果 |
| env_separate_rigid | `bool` | `False` | 是否将环境物体与刚性物体分开渲染 |
| background_color | `tuple` | `(0.04, 0.08, 0.12)` | 背景颜色 (RGB 格式，范围 0.0-1.0) |
| ambient_light | `tuple` | `(0.1, 0.1, 0.1)` | 环境光强度 (RGB 格式，范围 0.0-1.0) |
| visualize_mpm_boundary | `bool` | `False` | 是否可视化 MPM 边界 |
| visualize_sph_boundary | `bool` | `False` | 是否可视化 SPH 边界 |
| visualize_pbd_boundary | `bool` | `False` | 是否可视化 PBD 边界 |
| segmentation_level | `str` | `link` | 分割级别，默认为 "link" |
| render_particle_as | `str` | `sphere` | 粒子渲染形状，默认为 "sphere" |
| particle_size_scale | `float` | `1.0` | 粒子大小缩放因子 |
| contact_force_scale | `float` | `0.01` | 接触力的可视化缩放因子 |
| n_support_neighbors | `int` | `12` | 支持邻居数量 |
| n_rendered_envs | `Optional[int]` | `None` | 渲染的环境数量 |
| rendered_envs_idx | `Optional[list]` | `None` | 要渲染的环境索引列表 |
| lights | `list` | `[{'type': 'directional', 'dir': (-1, -1, -1), 'color': (1.0, 1.0, 1.0), 'intensity': 5.0}]` | 灯光配置列表 |

```{eval-rst}  
.. autoclass:: genesis.options.VisOptions
    :show-inheritance:
```
