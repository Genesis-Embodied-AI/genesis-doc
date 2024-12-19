# 📸 Visualization & Rendering

Genesis's visualization system is managed by the `visualizer` of the scene you just created (i.e. `scene.visualizer`). There are two ways for visualizing the scene: 1). using the interactive viewer that runs in a separate thread, and 2). by manually adding cameras to the scene and render images using the camera.


## Viewer
If you are connected to a display, you can visualize the scene using the interactive viewer. Genesis uses different `options` groups to configure different components in the scene. To configure the viewer, you can change the parameters in `viewer_options` when creating the scene. In addition, we use `vis_options` to specify visualization-related properties, which will be shared by the viewer and cameras (that we will add very soon).

Create a scene with a more detailed viewer and vis setting (this looks a bit complex, but it's just for illustration purposes):
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
        show_world_frame = True, # visualize the coordinate frame of `world` at its origin
        world_frame_size = 1.0, # length of the world frame in meter
        show_link_frame  = False, # do not visualize coordinate frames of entity links
        show_cameras     = False, # do not visualize mesh and frustum of the cameras added
        plane_reflection = True, # turn on plane reflection
        ambient_light    = (0.1, 0.1, 0.1), # ambient light setting
    ),
    renderer = gs.renderers.Rasterizer(), # using rasterizer for camera rendering
)
```
Here we can specify the pose and fov of the viewer camera. The viewer will run as fast as possible if `max_FPS` is set to `None`. If `res` is set to None, genesis will automatically create a 4:3 window with the height set to half of your display height. Also note that in the above setting, we set to use rasterization backend for camera rendering. Genesis provides two rendering backends: `gs.renderers.Rasterizer()` and `gs.renderers.RayTracer()`. The viewer always uses the rasterizer. By default, camera also uses rasterizer.


Once the scene is created, you can access the viewer object via `scene.visualizer.viewer`, or simply `scene.viewer` as a shortcut. You can query or set the viewer camera pose:
```python
cam_pose = scene.viewer.camera_pose

scene.viewer.set_camera_pose(cam_pose)
```

## Camera & Headless Rendering
Now let's manually add a camera object to the scene. Cameras are not connected to the viewer or the display, and returns rendered images only when you need it. Therefore, camera works in headless mode.

```python
cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)
```
If `GUI=True`, each camera will create an opencv window to dynamically display the rendered image. Note that this is different from the viewer GUI.

Then, once we build the scene, we can render images using the camera. Our camera supports rendering rgb image, depth, segmentation mask and surface normals. By default, only rgb is rendered, and you can turn other modes on by setting the parameters when calling `camera.render()`:

```python
scene.build()

# render rgb, depth, segmentation mask and normal map
rgb, depth, segmentation, normal = cam.render(depth=True, segmentation=True, normal=True)
```

If you used `GUI=True` and have a display connected, you should be able to see 4 windows now. (Sometimes opencv windows comes with extra delay, so you can call extra `cv2.waitKey(1)` if the windows are black, or simply call `render()` again to refresh the window.)
```{figure} ../../_static/images/multimodal.png
```

**Record videos using camera**

Now, let's only render rgb images, and move the camera around and record a video. Genesis provides a handy util for recording videos:
```python
# start camera recording. Once this is started, all the rgb images rendered will be recorded internally
cam.start_recording()

import numpy as np
for i in range(120):
    scene.step()

    # change camera position
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    
    cam.render()

# stop recording and save video. If `filename` is not specified, a name will be auto-generated using the caller file name.
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```
You will have the video saved to `video.mp4`:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/cam_record.mp4" type="video/mp4">
</video>


Here is the full code script covering everything discussed above:
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

# render rgb, depth, segmentation, and normal
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
## Photo-realistic Ray Tracing Rendering
Genesis provides a raytracing rendering backend for photorealistic rendering. You can easily switch to using this backend by setting `renderer=gs.renderers.RayTracer()` when creating the scene. This camera allows more parameter adjustment, such as `spp`, `aperture`, `model`, etc. Tutorial coming soon.