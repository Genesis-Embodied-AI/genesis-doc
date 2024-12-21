# 📸 可视化与渲染

Genesis的可视化系统由您刚创建的场景的`visualizer`管理（即`scene.visualizer`）。有两种方式来可视化场景：1）使用在单独线程中运行的交互式查看器，2）手动向场景添加相机并使用相机渲染图像。

## 查看器

如果您连接了显示器，可以使用交互式查看器来可视化场景。Genesis使用不同的`options`组来配置场景中的不同组件。要配置查看器，可以在创建场景时更改`viewer_options`中的参数。此外，我们使用`vis_options`来指定与可视化相关的属性，这些属性将由查看器和相机共享（我们很快会添加相机）。

创建一个具有更详细查看器和可视化设置的场景（这看起来有点复杂，但只是为了说明目的）：

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
        show_world_frame = True, # 可视化`world`在其原点的坐标系
        world_frame_size = 1.0, # 世界坐标系的长度（米）
        show_link_frame  = False, # 不可视化实体链接的坐标系
        show_cameras     = False, # 不可视化添加的相机的网格和视锥
        plane_reflection = True, # 打开平面反射
        ambient_light    = (0.1, 0.1, 0.1), # 环境光设置
    ),
    renderer = gs.renderers.Rasterizer(), # 使用光栅化器进行相机渲染
)
```

在这里我们可以指定查看器相机的姿态和视场角。如果`max_FPS`设置为`None`，查看器将尽可能快地运行。如果`res`设置为None，Genesis将自动创建一个4:3的窗口，高度设置为显示器高度的一半。还要注意，在上述设置中，我们设置使用光栅化后端进行相机渲染。Genesis提供了两种渲染后端：`gs.renderers.Rasterizer()`和`gs.renderers.RayTracer()`。查看器始终使用光栅化器。默认情况下，相机也使用光栅化器。

一旦场景创建完成，您可以通过`scene.visualizer.viewer`或简写`scene.viewer`访问查看器对象。您可以查询或设置查看器相机姿态：

```python
cam_pose = scene.viewer.camera_pose()

scene.viewer.set_camera_pose(cam_pose)
```

## 相机与无头渲染

现在让我们手动向场景添加一个相机对象。相机不连接到查看器或显示器，仅在您需要时返回渲染的图像。因此，相机在无头模式下工作。

```python
cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)
```

如果`GUI=True`，每个相机将创建一个opencv窗口以动态显示渲染的图像。请注意，这与查看器GUI不同。

然后，一旦我们构建场景，我们可以使用相机渲染图像。我们的相机支持渲染rgb图像、深度图、分割掩码和表面法线。默认情况下，仅渲染rgb，您可以通过在调用`camera.render()`时设置参数来打开其他模式：

```python
scene.build()

# 渲染rgb、深度、分割掩码和法线图
rgb, depth, segmentation, normal = cam.render(depth=True, segmentation=True, normal=True)
```

如果您使用了`GUI=True`并连接了显示器，您现在应该能看到4个窗口。（有时opencv窗口会有额外的延迟，所以如果窗口是黑色的，您可以调用额外的`cv2.waitKey(1)`，或者简单地再次调用`render()`来刷新窗口。）

```{figure} ../../_static/images/multimodal.png
```

**使用相机录制视频**

现在，让我们仅渲染rgb图像，并移动相机并录制视频。Genesis提供了一个方便的工具来录制视频：

```python
# 开始相机录制。一旦开始，所有渲染的rgb图像将被内部记录
cam.start_recording()

import numpy as np
for i in range(120):
    scene.step()

    # 改变相机位置
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    
    cam.render()

# 停止录制并保存视频。如果未指定`filename`，将使用调用文件名自动生成名称。
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```

您将视频保存到`video.mp4`：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/cam_record.mp4" type="video/mp4">
</video>

以下是涵盖上述所有内容的完整代码脚本：

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

## 逼真的光线追踪渲染

Genesis提供了一个光线追踪渲染后端，用于逼真的渲染。您可以通过在创建场景时设置`renderer=gs.renderers.RayTracer()`轻松切换到使用此后端。此相机允许更多参数调整，例如`spp`、`aperture`、`model`等。教程即将推出。
