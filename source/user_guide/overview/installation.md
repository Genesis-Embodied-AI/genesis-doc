# Installation

Genesis World installs from PyPI in two steps: install PyTorch, then install Genesis World. It runs on Linux, macOS, and Windows, on CPU and on CUDA and non-CUDA GPUs.

## Install

1. Install PyTorch by following the [official instructions](https://pytorch.org/get-started/locally/) for your platform and CUDA version.

2. Install Genesis World from PyPI:

   ```bash
   pip install genesis-world
   ```

Once installed, initialize the library with `gs.init()`. See {doc}`Initialization and backends </user_guide/configuration/initialization>` for backend selection, precision, and reproducibility.

:::{note}
To run on CUDA, make sure a matching NVIDIA driver is installed on your machine.
:::

## Prerequisites

- **Python:** 3.10 to 3.13 (`>=3.10,<3.14`).
- **Operating system:** Linux, macOS, or Windows. Linux with a CUDA-compatible GPU gives the best performance.

Genesis World is cross-platform across CPU, CUDA GPUs, and non-CUDA GPUs. The following combinations are supported:

| OS | GPU | GPU simulation | CPU simulation | Interactive viewer | Headless rendering |
|---|---|:---:|:---:|:---:|:---:|
| Linux | Nvidia | ✅ | ✅ | ✅ | ✅ |
| Linux | AMD | ✅ | ✅ | ✅ | ✅ |
| Linux | Intel | ✅ | ✅ | ✅ | ✅ |
| Windows | Nvidia | ✅ | ✅ | ✅ | ✅ |
| Windows | AMD | ✅ | ✅ | ✅ | ✅ |
| Windows | Intel | ✅ | ✅ | ✅ | ✅ |
| macOS | Apple Silicon | ✅ | ✅ | ✅ | ✅ |

## Optional components

### Surface reconstruction

To render particle-based entities (fluids, deformables, and the like) as smooth surfaces, Genesis World reconstructs a mesh from the internal particle representation. [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf) is supported out of the box. `ParticleMesher`, an in-house OpenVDB-based tool, is faster but produces lower-quality surfaces; enable it by adding its library to your path:

```bash
echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc
```

### Ray-tracing renderer

For photorealistic stills, Genesis World includes a ray-tracing renderer built on [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute). It is built from source; see {doc}`/user_guide/rendering/index` for setup. For new work, prefer the {doc}`Nyx renderer </user_guide/rendering/nyx_renderer>`.

### USD assets

To load USD assets into scenes, see the [USD import setup](../assets/usd_import.md#installation).

## Troubleshooting

### `Genesis hasn't been initialized`

Importing an engine submodule before calling `gs.init()` raises this error:

```python
genesis.GenesisException: Genesis hasn't been initialized. Did you call `gs.init()`?
```

Engine submodules must be imported after initialization so they can configure low-level Quadrants features such as the fast-cache mechanism and dynamic array mode. This is rarely a problem in practice, because engine classes are not meant to be instantiated by hand. If you need to import one for type checking, guard the import:

```python
from typing import TYPE_CHECKING

import genesis as gs

if TYPE_CHECKING:
    from genesis.engine.entities.drone_entity import DroneEntity
```

### Circular import error

Importing `genesis` fails with a circular import when the current directory is the Genesis World source directory and the package is installed in non-editable mode (from PyPI or from source). Either move out of the source directory before running Python, or switch to an editable install: uninstall `genesis-world`, then run `pip install -e ".[render]"` inside the source directory.

### Slow rendering on native Ubuntu (CPU fallback)

If `cam.render()` or the viewer becomes extremely slow, the system may be silently falling back to MESA (CPU) rendering instead of using the GPU. Genesis World relies on PyRender and EGL for GPU offscreen rendering; if `libnvidia-egl` is not set up correctly, rendering falls back to software even when the GPU is otherwise accessible.

To ensure GPU rendering is active:

1. Install the NVIDIA GL libraries:

   ```bash
   sudo apt update && sudo apt install -y libnvidia-gl-525
   ```

2. Check that EGL points to the NVIDIA driver:

   ```bash
   ldconfig -p | grep EGL
   ```

   You want to see `libEGL_nvidia.so.0`. You may also see `libEGL_mesa.so.0`; some systems handle both, but if rendering is slow, remove Mesa.

3. Optionally remove MESA to prevent fallback, then recheck:

   ```bash
   sudo apt remove -y libegl-mesa0 libegl1-mesa libglx-mesa0
   ldconfig -p | grep EGL
   ```

4. In minimal or containerized environments, the NVIDIA EGL ICD config may be missing. Confirm `/usr/share/glvnd/egl_vendor.d/10_nvidia.json` exists and contains:

   ```json
   {
       "file_format_version": "1.0.0",
       "ICD": {
           "library_path": "libEGL_nvidia.so.0"
       }
   }
   ```

   If it is missing, create it, and add the CUDA runtime symlink if needed:

   ```bash
   ln -s /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
   ```

5. Genesis World tries EGL by default, so you usually do not need to set `PYOPENGL_PLATFORM`. In custom setups (Docker, headless servers) these variables can help:

   ```bash
   export NVIDIA_DRIVER_CAPABILITIES=all
   export PYOPENGL_PLATFORM=egl
   ```

### Black rendering window in Docker on Windows 11 (WSL2)

On machines with an NVIDIA GPU, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). If rendering still fails inside a Docker container based on the Genesis image, add the WSL libraries to the container's library search path:

```bash
docker run --gpus all --rm -it \
    -e DISPLAY=$DISPLAY \
    -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    genesis
```

### OpenGL error in an Ubuntu VM on Windows 11 (WSL2)

On machines with an NVIDIA GPU, force GPU-accelerated rendering from inside the VM:

```bash
export LIBGL_ALWAYS_INDIRECT=0
export GALLIUM_DRIVER=d3d12
export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
```

If that does not work, install the latest OSMesa and enforce direct rendering:

```bash
sudo add-apt-repository ppa:kisak/kisak-mesa
sudo apt update && sudo apt upgrade
export LIBGL_ALWAYS_INDIRECT=0
```

Use `glxinfo -B` to check which OpenGL vendor is active. As a last resort, force software rendering with `export LIBGL_ALWAYS_SOFTWARE=1`.

### Quadrants falls back to CPU in an Ubuntu VM on Windows 11 (WSL2)

If PyTorch initializes on CUDA but Quadrants falls back to CPU (or Vulkan) with `libcuda.so lib not found`, the CUDA libraries are not on the library path. Confirm they are present and add them:

```bash
ls /usr/lib/wsl/lib/
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH
```
