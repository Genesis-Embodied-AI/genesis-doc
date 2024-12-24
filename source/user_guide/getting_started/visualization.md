# 📸 可视化与渲染

Genesis的可视化系统由场景的`visualizer`管理（即`scene.visualizer`）。可以通过两种方式来可视化场景：

1. 使用独立线程运行的交互式查看器
2. 手动添加相机并渲染图像

## 查看器

连接显示器后可使用交互式查看器来查看场景。Genesis用不同的`options`组来配置场景中的组件。可以通过以下方式配置:

- 创建场景时修改`viewer_options`中的参数
- 使用`vis_options`设置可视化属性(查看器和相机共用)

下面创建一个详细配置的场景:

```python
scene = gs.Scene(
    show_viewer    = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True, # 显示原点坐标系
        world_frame_size = 1.0, # 坐标系长度(米)
        show_link_frame  = False, # 不显示实体链接坐标系 
        show_cameras     = False, # 不显示相机网格和视锥
        plane_reflection = True, # 开启平面反射
        ambient_light    = (0.1, 0.1, 0.1), # 环境光
    ),
    renderer = gs.renderers.Rasterizer(), # 使用光栅化渲染器
)
```

这里可以设置:

- 查看器相机的位置和视场角
- 如果`max_FPS`为`None`,查看器会全速运行
- 如果`res`为None,会创建一个4:3窗口,高度为显示器一半
- Genesis提供两种渲染器:`Rasterizer`和`RayTracer`
- 查看器固定使用光栅化,相机默认也使用光栅化

场景创建后,可以通过`scene.visualizer.viewer`或`scene.viewer`访问查看器:

```python
cam_pose = scene.viewer.camera_pose()
scene.viewer.set_camera_pose(cam_pose)
```

## 相机与离线渲染

可以手动添加相机对象进行离线渲染:

```python
cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)
```

设置`GUI=True`会为每个相机创建opencv窗口显示渲染结果。

构建场景后就可以渲染图像了。相机支持:

- RGB图像
- 深度图
- 分割掩码
- 表面法线

默认只渲染RGB,可以通过参数开启其他模式:

```python
scene.build()

# 渲染所有类型
rgb, depth, segmentation, normal = cam.render(depth=True, segmentation=True, normal=True)
```

如果使用`GUI=True`且连接了显示器,会看到4个窗口。(如果窗口是黑的,可以多调用一次`cv2.waitKey(1)`或`render()`来刷新)

```{figure} ../../_static/images/multimodal.png
```

### 录制视频

下面演示如何移动相机并录制视频:

```python
# 开始录制
cam.start_recording()

import numpy as np
for i in range(120):
    scene.step()

    # 移动相机
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    
    cam.render()

# 停止录制并保存视频
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```

将视频保存到`video.mp4`：

![video](../../_static/videos/cam_record.mp4)

完整代码如下:

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    show_viewer = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True,
        world_frame_size = 1.0,
        show_link_frame  = False,
        show_cameras     = False,
        plane_reflection = True,
        ambient_light    = (0.1, 0.1, 0.1),
    ),
    renderer=gs.renderers.Rasterizer(),
)

plane = scene.add_entity(
    gs.morphs.Plane(),
)
franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

cam = scene.add_camera(
    res    = (640, 480),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False,
)

scene.build()

# 渲染rgb、深度、分割掩码和法线图
# rgb, depth, segmentation, normal = cam.render(rgb=True, depth=True, segmentation=True, normal=True)

cam.start_recording()
import numpy as np

for i in range(120):
    scene.step()
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    cam.render()
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```

## 光线追踪渲染

Genesis提供光线追踪渲染器用于真实感渲染。创建场景时设置`renderer=gs.renderers.RayTracer()`即可切换。支持调节`spp`、`aperture`、`model`等参数,教程即将发布。
