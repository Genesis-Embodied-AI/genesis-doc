# Installation

## Install

1. Install PyTorch. Refer to the [official instructions](https://pytorch.org/get-started/locally/) for your platform and CUDA version.

2. Install Genesis World from PyPI:

   ```bash
   pip install genesis-world
   ```

Once installed, initialize the library with `gs.init()`. See {doc}`Initialization and backends </user_guide/configuration/initialization>` for backend selection, precision, and reproducibility.

:::{note}
To run on CUDA, ensure a matching NVIDIA driver is installed on your machine.
:::

## Prerequisites

- **Python:** 3.12 to 3.14 (`>=3.12,<3.15`).
- **Operating system (OS):** Linux, macOS, or Windows. Linux with a CUDA-compatible GPU gives the best performance.

Genesis World is cross-platform across CPUs and GPUs: 

- NVIDIA through CUDA (`gs.cuda`)

- AMD through ROCm (`gs.amdgpu`)

- Apple Silicon through Metal (`gs.metal`), with a CPU backend (`gs.cpu`) available everywhere. 

`gs.gpu `selects the GPU backend your machine has. If it has none, `gs.gpu` falls back to `gs.cpu` and shows a warning. An Intel GPU drives the viewer and offscreen rendering but has no simulation backend. On a machine with an Intel GPU, run the physics on `gs.cpu`. 

Genesis World supports these combinations:

| OS          | GPU           | GPU simulation | CPU simulation | Interactive viewer | Headless rendering |
| :---------- | :------------ | :------------: | :------------: | :----------------: | :----------------: |
| **Linux**   | NVIDIA        |       ✓        |       ✓        |         ✓          |         ✓          |
|             | AMD           |       ✓        |       ✓        |         ✓          |         ✓          |
|             | Intel         |       ✗        |       ✓        |         ✓          |         ✓          |
| **Windows** | NVIDIA        |       ✓        |       ✓        |         ✓          |         ✓          |
|             | AMD           |       ✓        |       ✓        |         ✓          |         ✓          |
|             | Intel         |       ✗        |       ✓        |         ✓          |         ✓          |
| **macOS**   | Apple Silicon |       ✓        |       ✓        |         ✓          |         ✓          |

:::{note}

GPU simulation on AMD through ROCm is experimental. It may be unstable, especially on Windows.

:::

## Optional components

These components add features that most setups do not need. Install one only if you use it.

### Surface reconstruction

Genesis World renders particle-based entities, such as fluids and deformables, as smooth surfaces. It reconstructs a mesh from the internal particle representation. The default backend is [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf). It extracts a smooth surface from the particle density, but requires all particles to share one radius. 

To use a different radius for each particle, set `recon_backend="levelset"` on the surface. This backend wraps the union of the particle spheres at the cost of a bumpier surface. Both backends work on every platform with no extra install. `recon_backend="openvdb"` is a deprecated alias of `"levelset"`.

### Ray-tracing renderer

Genesis World includes a ray-tracing renderer built on [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute) for photorealistic stills. It is built from source. See {doc}`/user_guide/rendering/cameras` for setup. For new work, refer to the {doc}`Nyx renderer </user_guide/rendering/nyx_renderer>`. Install it with `pip install gs-nyx`.

### IPC coupler

The [libuipc](https://github.com/spiriMirror/libuipc)-based IPC coupler (`gs.options.IPCCouplerOptions`) needs `pip install pyuipc`. It is available on Linux and Windows x86 with an NVIDIA GPU. See {doc}`/user_guide/physics/coupling/ipc_coupler`.

### USD assets

To load USD assets into scenes, see the [USD import setup](../assets/usd_import.md#installation).

## Troubleshooting

### `"Genesis hasn't been initialized" `

Creating a scene or a morph before calling `gs.init()` raises this error:

```text
genesis.GenesisException: Genesis hasn't been initialized. Did you call `gs.init()`?
```

Call `gs.init()` first. It selects the backend and configures low-level Quadrants features such as the fast-cache mechanism and dynamic array mode.

### Circular import error

`import genesis` fails with a circular import error when both of these are true:

- Your current directory is the Genesis World source directory.

- You installed the package in non-editable mode, from PyPI or from source.

To fix it, do one of the following:

- Move out of the source directory before you run Python.

- Switch to an editable install:

  1. Uninstall `genesis-world`.

  2. Inside the source directory, run `pip install -e ".[render]"`.

### Slow rendering on native Ubuntu (CPU fallback)

If `cam.render()` or the viewer becomes extremely slow, the system may be silently falling back to MESA (CPU) rendering instead of using the GPU. Genesis World uses PyRender and EGL for GPU offscreen rendering. If `libnvidia-egl` is not set up correctly, rendering falls back to software even when the GPU is otherwise accessible.

To ensure GPU rendering is active:

1. Install the NVIDIA GL libraries:

   ```bash
   sudo apt update && sudo apt install -y libnvidia-gl-525
   ```

2. Check that EGL points to the NVIDIA driver:

   ```bash
   ldconfig -p | grep EGL
   ```

   The output should include libEGL_nvidia.so.0. It may also include libEGL_mesa.so.0. Some systems handle both, but if rendering is slow, remove Mesa.

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

5. Genesis World selects the offscreen OpenGL backend for your operating system (EGL on Linux, CGL on macOS, and pyglet elsewhere). You usually do not need to set `PYOPENGL_PLATFORM`. To override that choice, set it to `egl`, `osmesa`, `cgl` (macOS only), or `pyglet`. In custom setups (Docker, headless servers) these variables can help:

   ```bash
   export NVIDIA_DRIVER_CAPABILITIES=all
   export PYOPENGL_PLATFORM=egl
   ```

### Black rendering window in Docker on Windows 11 (WSL2)

On machines with an NVIDIA GPU, install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). If rendering still fails inside a Docker container, add the WSL libraries to the container's library search path:

```bash
docker run --gpus all --rm -it \
    -e DISPLAY=$DISPLAY \
    -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    <...>
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

If PyTorch initializes on CUDA but Quadrants falls back to CPU with `libcuda.so lib not found`, the CUDA libraries are not on the library path. Confirm they are present and add them:

```bash
ls /usr/lib/wsl/lib/
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH
```
