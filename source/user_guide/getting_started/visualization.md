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

Genesis provides a ray tracing rendering backend for photorealistic rendering. You can easily switch to using this backend by setting `renderer=gs.renderers.RayTracer()` when creating the scene. This camera allows more parameter adjustment, such as `spp`, `aperture`, `model`, etc.

### Setup

Tested on
- Ubuntu 22.04, CUDA 12.4, python 3.9

Get submodules, specifically `genesis/ext/LuisaRender`.
```bash
# inside Genesis/
git submodule update --init --recursive
pip install -e ".[render]"
```
Install/upgrad g++ and gcc (to) version >= 11.
```bash
sudo apt install build-essential manpages-dev software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update && sudo apt install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

# verify version
g++ --version
gcc --version
```
Install CMake if your local version does not meet the required version. We use `snap` instead of `apt` because we need CMake version >= 3.26. However, remember to use the correct cmake. You may have `/usr/local/bin/cmake` but the `snap` installed package is at `/snap/bin/cmake` (or `/usr/bin/snap`). Please double check the order of binary path via `echo $PATH`.
```bash
sudo snap install cmake --classic
cmake --version
```
Install dependencies,
```bash
sudo apt install libvulkan-dev xorg-dev # Vulkan, X11 & RandR
sudo apt-get install uuid-dev # UUID 
sudo apt-get install zlib1g-dev # zlib
```

If you do not have sudo, the following commands also install the required dependencies in your conda environments:
```bash
conda install -c conda-forge gcc=11.4 gxx=11.4 
conda install -c conda-forge cmake=3.26.1
conda install -c conda-forge vulkan-tools vulkan-headers xorg-xproto # Vulkan, X11 & RandR
conda install -c conda-forge libuuid # UUID
conda install -c conda-forge zlib # zlib
```

Build `LuisaRender`. Remember to use the correct cmake. By default, we use OptiX denoiser (For CUDA backend only). If you need OIDN denoiser, append `-D LUISA_COMPUTE_DOWNLOAD_OIDN=ON`.
```bash
cd genesis/ext/LuisaRender
cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D LUISA_RENDER_BUILD_TESTS=OFF # remember to check python version
cmake --build build -j $(nproc)
```

If you really struggle getting the build, we have some build [here](https://drive.google.com/drive/folders/1Ah580EIylJJ0v2vGOeSBU_b8zPDWESxS?usp=sharing) and you can check if your machine happens to have the same setup. The naming follows `build_<commit-tag>_cuda<version>_python<version>`. Download the one that matches your system, rename to `build/` and put it in `genesis/ext/LuisaRender`.

Finally, you can run the example,
```bash
cd examples/rendering
python demo.py
```
You should be able to get
```{figure} ../../_static/images/raytracing_demo.png
```

## Batch rendering with gs-madrona

Genesis provides a high-throughput batch rendering backend via gs-madrona. You can easily switch to gs-madrona backend by setting `renderer=gs.renderers.BatchRenderer(use_rasterizer=True/False)`

### Pre-requisite
Please first install the latest version of Genesis to date following the [official README instructions](https://github.com/Genesis-Embodied-AI/Genesis#quick-installation).

### Easy install (x86 only)
Pre-compiled binary wheels for Python>=3.10 are available on PyPI. They can be installed using any Python package manager (e.g. `uv` or `pip`):
```sh
pip install gs-madrona
```

### Build from source
```sh
pip install .
```

### Testing (Optional)
1. Clone Genesis Simulator repository if not already done
```sh
git clone https://github.com/Genesis-Embodied-AI/Genesis.git
```

2. Run the following example script provided with Genesis
```sh
python Genesis/examples/rigid/single_franka_batch_render.py
```

All the generated images will be stored in the current directory under `./image_output`.

2. To use ray tracer, change the `use_rasterizer=False` in `single_franka_batch_render.py`
```
renderer = gs.options.renderers.BatchRenderer(
    use_rasterizer=False,
)
```

### FAQ
- Installed libraries still undetected when running `cmake -S . -B build`,
    You can manually instruct CMake to detect the dependencies by explicitly setting options such as `XXX_INCLUDE_DIR`, e.g., `ZLIB_INCLUDE_DIR=/path/to/include`. For conda environments, `XXX_INCLUDE_DIR` typically follows the format `/home/user/anaconda3/envs/genesis/include`.
- Pybind error when doing `cmake -S . -B build`,
    ```bash
    CMake Error at src/apps/CMakeLists.txt:12 (find_package):
    By not providing "Findpybind11.cmake" in CMAKE_MODULE_PATH this project has
    asked CMake to find a package configuration file provided by "pybind11",
    but CMake did not find one.

    Could not find a package configuration file provided by "pybind11" with any
    of the following names:

        pybind11Config.cmake
        pybind11-config.cmake
    ```
    You probably forget to do `pip install -e ".[render]"`. Alternatively, you can simply do `pip install "pybind11[global]"`.
- CUDA runtime compilation error when running `cmake -S . -B build`,
    ```bash
    /usr/bin/ld: CMakeFiles/luisa-cuda-nvrtc-standalone-compiler.dir/cuda_nvrtc_compiler.cpp.o: in function `main':
    cuda_nvrtc_compiler.cpp:(.text.startup+0x173): undefined reference to `nvrtcGetOptiXIRSize'
    /usr/bin/ld: cuda_nvrtc_compiler.cpp:(.text.startup+0x197): undefined reference to `nvrtcGetOptiXIR'
    ```
    You need to install "system-wise" cuda-toolkit ([official installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)). You first check the cuda-toolkit,
    ```bash
    nvcc --version # this should be the consistent with you cuda version from nvidia-smi
    which nvcc # just to check you are using the cuda-toolkit you expected
    ```
    If you don't get proper output from `nvcc`, please follow the official cuda-toolkit installation guide. Yet, just as an example of installing cuda-toolkit for cuda-12.4. Download installer as in [here](https://developer.nvidia.com/cuda-12-4-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local).
    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2204-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get -y install cuda-toolkit-12-4
    ```
    Remember to set binary and runtime library path. In `~/.bashrc`, add the following (note that we append the CUDA path at the end since there are also another `gcc` and `g++` in `/usr/local/cuda-12.4/bin` and may not be version 11, which is required for the build),
    ```bash
    PATH=${PATH:+${PATH}:}/usr/local/cuda-12.4/bin
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```
    Remember to either restart the terminal or do `source ~/.bashrc`. Another type of error is,
    ```bash
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_fatal_printf@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_symbind_alt@GLIBC_PRIVATE'
    <your-env-path>/genesis-test1/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_exception_create@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__nptl_change_stack_perm@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__tunable_get_val@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_preinit@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_find_dso_for_object@GLIBC_PRIVATE'
    ```
    This may be due to the cuda-toolkit in your conda environment. Please do the following and install the system-wise CUDA,
    ```bash
    which nvcc
    conda uninstall cuda-toolkit
    ```
    Alternatively, you can add your conda library path to the runtime library path,
    ```bash
    ls $CONDA_PREFIX/lib/libcudart.so # you should have this

    # inside you ~/.bashrc, add
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```
    Lastly, remember to clear the build after doing the above fixed,
    ```bash
    rm -r build
    ```
- C/CXX Compiler error at `cmake -S . -B build`,
    ```bash
    CMake Error at /snap/cmake/1435/share/cmake-3.31/Modules/CMakeDetermineCCompiler.cmake:49 (message):
    Could not find compiler set in environment variable CC:

    /home/tsunw/miniconda3/envs/genesis-test1/bin/x86_64-conda-linux-gnu-cc.
    Call Stack (most recent call first):
    CMakeLists.txt:21 (project)


    CMake Error: CMAKE_C_COMPILER not set, after EnableLanguage
    CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
    ```
    You are probably not using `gcc` and `g++` version 11. Please double check (i) the version (ii) if the binary points to the path as expected (iii) the order of your binary path,
    ```bash
    gcc --version
    g++ --version
    which gcc
    which g++
    echo $PATH # e.g., /usr/local/cuda-12.4/bin/gcc (version = 10.5) shouldn't be in front of /usr/bin/gcc (version = 11 if you install properly with apt)
    ```
- Import error when running `examples/rendering/demo.py`,
    ```bash
    [Genesis] [11:29:47] [ERROR] Failed to import LuisaRenderer. ImportError: /home/tsunw/miniconda3/envs/genesis-test1/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.30' not found (required by /home/tsunw/workspace/Genesis/genesis/ext/LuisaRender/build/bin/liblc-core.so)
    ```
    Conda’s `libstdc++.so.6` doesn’t support 3.4.30. You need to move system’s into conda ([reference](https://stackoverflow.com/a/73708979)).
    ```bash
    cd $CONDA_PREFIX/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```
- Assertion 'lerror’ failed: Failed to write to the process: Broken pipe: You may need to use CUDA of the same version as compiled.
