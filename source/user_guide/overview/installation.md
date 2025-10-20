# 🛠️ Installation
## Prerequisites
* **Python**: >=3.10,<3.14
* **OS**: Linux (*recommended*) / MacOS / Windows

:::{note}
Genesis is designed to be ***cross-platform***, supporting backend devices including *CPU*, *CUDA GPU* and *non-CUDA GPU*. That said, it is recommended to use **Linux** platform with **CUDA-compatible GPU** to achieve the best performance.
:::

Supported features on various systems are as follows:
<div style="text-align: center;">

| OS  | GPU Device        | GPU Simulation | CPU Simulation | Interactive Viewer | Headless Rendering |
| ------- | ----------------- | -------------- | -------------- | ---------------- | ------------------ |
| Linux   | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| Windows | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| MacOS   | Apple Silicon     | ✅             | ✅             | ✅               | ✅                 |

</div>

## Installation
1. Install **PyTorch** following the [official instructions](https://pytorch.org/get-started/locally/).

2. Install Genesis via PyPI:
    ```bash
    pip install genesis-world
    ```

:::{note}
If you are using Genesis with CUDA, make sure appropriate nvidia-driver is installed on your machine.
:::

## (Optional) Surface Reconstruction
If you need fancy visuals for visualizing particle-based entities (fluids, deformables, etc.), you typically need to reconstruct the mesh surface using the internal particle-based representation. For this purpose, [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf), a state-of-the-art surface reconstruction, is supported out-of-the-box. Alternatively, we also provide `ParticleMesher`, our own openVDB-based surface reconstruction tool, which is faster but lower quantity:
```bash
echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc
```

## (Optional) Ray Tracing Renderer

If you need photo-realistic visuals, Genesis has a built-in a ray-tracing (path-tracing) based renderer developped using [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute), a high-performance domain specific language designed for rendering. See [Visualization & Rendering](../getting_started/visualization.md) for setup.

## (Optional) USD Assets 

If you need load USD assets as `gs.morphs.Mesh` into Genesis scene, you need to install the dependencies through:
```bash
pip install -e .[usd]
# Omniverse kit is used for USD material baking. Only available for Python 3.10 and GPU backend now.
# If USD baking is disabled, Genesis only parses materials of "UsdPreviewSurface".
pip install --extra-index-url https://pypi.nvidia.com/ omniverse-kit
# To use USD baking, you should set environment variable `OMNI_KIT_ACCEPT_EULA` to accept the EULA.
# This is a one-time operation, if accepted, it will not ask again.
export OMNI_KIT_ACCEPT_EULA=yes
```

## Troubleshooting

### Import Error

#### 'Genesis hasn't been initialized'

Genesis is not initialized, trying to import any engine-related submodule will raise an exception, e.g.;
```python
Traceback (most recent call last):
  File "/home/jeremy/Downloads/Genesis_Jeremy/examples/./init_error.py", line 3, in <module>
    from genesis.engine.entities import RigidEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/__init__.py", line 1, in <module>
    from .avatar_entity import AvatarEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/avatar_entity/__init__.py", line 1, in <module>
    from .avatar_entity import AvatarEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/avatar_entity/avatar_entity.py", line 6, in <module>
    from ..rigid_entity import RigidEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/rigid_entity/__init__.py", line 1, in <module>
    from .rigid_entity import RigidEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/rigid_entity/rigid_entity.py", line 14, in <module>
    from genesis.utils import array_class
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/array_class.py", line 13, in <module>
    gs.raise_exception("Genesis hasn't been initialized. Did you call `gs.init()`?")
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/misc.py", line 42, in raise_exception
    raise gs.GenesisException(msg)
genesis.GenesisException: Genesis hasn't been initialized. Did you call `gs.init()`?
```

This error is bug but expected. Any engine-related submodules must be imported after initializing Genesis to have the opportunity to configure low-level GsTaichi features such as fast cache mechanism or Gstaichi dynamic array mode. In practice, this limitation should not be a blocker for anybody, because engine-related classes are not meant to be instantiated manually. Still, it may be convenient to import them for type checking. If so, just use typing checking guard, e.g.:
```python
from typing import TYPE_CHECKING

import genesis as gs
if TYPE_CHECKING:
    from genesis.engine.entities.drone_entity import DroneEntity
```

#### Circular Import Error

Python would fail to (circular) import Genesis if the current directory is the source directory of Genesis. This is likely due to Genesis being installed WITHOUT enabling editable mode, either from PyPI Package Index or from source. The obvious workaround is moving out of the source directory of Genesis before running Python. The long-term solution is simply switching to editable install mode: first uninstall Python package `genesis-world`, then run `pip install -e '.[render]'` inside the source directory of Genesis.

### [Native Ubuntu] Slow Rendering (CPU aka. Software Fallback)

Sometimes, when using `cam.render()` or viewer-related functions in Genesis, rendering becomes extremely slow. This is **not a Genesis issue**. Genesis relies on PyRender and EGL for GPU-based offscreen rendering. If your system isn’t correctly set up to use `libnvidia-egl`, it may **silently fall back to MESA (CPU) rendering**, severely affecting performance.

Even if the GPU appears accessible, your system might still default to CPU rendering unless explicitly configured.

---

#### ✅ Ensure GPU Rendering is Active

1. **Install NVIDIA GL libraries**
   ```bash
   sudo apt update && sudo apt install -y libnvidia-gl-525
   ```

2. **Check if EGL is pointing to the NVIDIA driver**
   ```bash
   ldconfig -p | grep EGL
   ```
   You should ideally see:
   ```
   libEGL_nvidia.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_nvidia.so.0
   ```

   ⚠️ You *may also see*:
   ```
   libEGL_mesa.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_mesa.so.0
   ```

   This is not always a problem — **some systems can handle both**.
   But if you're experiencing **slow rendering**, it's often best to remove Mesa.

3. **(Optional but recommended)** Remove MESA to prevent fallback:
   ```bash
   sudo apt remove -y libegl-mesa0 libegl1-mesa libglx-mesa0
   ```
   Then recheck:
   ```bash
   ldconfig -p | grep EGL
   ```
   ✅ You should now only see `libEGL_nvidia.so.0`.

4. **(Optional – for edge cases)** Check if the NVIDIA EGL ICD config file exists

    In most cases, this file should already be present if your NVIDIA drivers are correctly installed. However, in some minimal or containerized environments (e.g., headless Docker images), you might need to manually create it if EGL initialization fails:
    ```bash
    cat /usr/share/glvnd/egl_vendor.d/10_nvidia.json
    ```
    Should contain:
    ```json
    {
        "file_format_version" : "1.0.0",
        "ICD" : {
            "library_path" : "libEGL_nvidia.so.0"
        }
    }
    ```

    If not, create it:
    ```bash
    bash -c 'cat > /usr/share/glvnd/egl_vendor.d/10_nvidia.json <<EOF
    {
        "file_format_version": "1.0.0",
        "ICD": {
            "library_path": "libEGL_nvidia.so.0"
        }
    }
    EOF'
    ```

    Similarly, some symlink may be missing for the CUDA runtime:
    ```bash
    ln -s /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
    ```

5. **Set global NVIDIA rendering environment variables**

Genesis tries EGL rendering by default, so in most environments you don’t need to manually set `PYOPENGL_PLATFORM`. However, setting these variables can help ensure stability in custom setups (e.g., Docker, headless servers):

   Add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   export NVIDIA_DRIVER_CAPABILITIES=all
   export PYOPENGL_PLATFORM=egl
   ```

   Reload:
   ```bash
   source ~/.bashrc  # or source ~/.zshrc
   ```

   Confirm:
   ```python
   import os
   print("[DEBUG] Using OpenGL platform:", os.environ.get("PYOPENGL_PLATFORM"))
   print("[DEBUG] NVIDIA capabilities:", os.environ.get("NVIDIA_DRIVER_CAPABILITIES"))
   ```

### [Docker Container (Genesis image) on Windows 11 via WSL2] Black Rendering Window

    For machines with Nvidia GPU, make sure that NVIDIA Container Toolkit is installed. The official guide is available [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

    Some users may still be experiencing rendering issues on Windows when running Genesis inside a Docker container based on Genesis image. This is generally fixed by adding WSL libraries to Linux's search path for dynamic libraries, which is specified by the environment variable `LD_LIBRARY_PATH`, i.e.:
    ```bash
    docker run --gpus all --rm -it \
    -e DISPLAY=$DISPLAY \
    -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    genesis
    ```

### [Ubuntu VM on Windows 11 via WSL2] OpenGL error

    For machines with Nvidia GPU, try to force GPU-accelerated rendering by exporting the following environment variables inside the Ubuntu VM:
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    export GALLIUM_DRIVER=d3d12
    export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
    ```

    If it does not work, try installing the latest version of OSMesa:
    ```bash
    sudo add-apt-repository ppa:kisak/kisak-mesa
    sudo apt update
    sudo apt upgrade
    ```
    Then, only enforce direct rendering:
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    ```

    At the point, `glxinfo` mesa utility can be used to determine which OpenGL vendor is being used by default, i.e.:
    ```bash
    glxinfo -B
    ```

    As a last resort, one can force CPU (aka. software) rendering using OSMesa if necessary as follows:
    ```bash
    export LIBGL_ALWAYS_SOFTWARE=1
    ```

### [Ubuntu VM on Windows 11 via WSL2] Taichi and Genesis do not find cudalib.so and falls back to CPU

After installing Pytorch and Genesis, Taichi falls back to CPU, while torch initalizes okay on CUDA.

Symptoms: 

- running `python -c "import torch; print(torch.zeros((3,), device='cuda'))"` outputs `tensor([0., 0., 0.], device='cuda:0')`
- but running `python -c "import gstaichi as ti; ti.init(arch=ti.gpu)"` outputs something like
    ```
    [W 06/18/25 12:47:56.784 14507] [cuda_driver.cpp:load_lib@36] libcuda.so lib not found.
    [Taichi] Starting on arch=vulkan
    ```

Fix:

- check if libcuda.so and other cuda libraries are in the lib folder with `ls /usr/lib/wsl/lib/`
- if so, update the library path with `export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH`
