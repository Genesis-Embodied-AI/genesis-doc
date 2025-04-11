# 🛠️ Installation
## Prerequisites
* **Python**: >=3.10,<3.13
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


## (Optional) Motion planning
Genesis integrated OMPL's motion planning functionalities and wraps it using a intuitive API for effortless motion planning. If you need the built-in motion planning capability, download pre-compiled OMPL wheel [here](https://github.com/ompl/ompl/releases/tag/prerelease), and then `pip install` it.

## (Optional) Surface reconstruction
If you need fancy visuals for visualizing particle-based entities (fluids, deformables, etc.), you typically need to reconstruct the mesh surface using the internal particle-based representation. We provide two options for this purpose:

1. [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf), a state-of-the-art surface reconstruction method for achieving this:
    ```bash
    cargo install splashsurf
    ```
2. ParticleMesher, our own openVDB-based surface reconstruction tool (faster but with not as smooth):
    ```bash
    echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
    source ~/.bashrc
    ```


## (Optional) Ray Tracing Renderer

If you need photo-realistic visuals, Genesis has a built-in a ray-tracing (path-tracing) based renderer developped using [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute), a high-performance domain specific language designed for rendering.

### 1. Get LuisaRender
The submodule LuisaRender is under `ext/LuisaRender`:
```bash
git submodule update --init --recursive
```
### 2. Dependencies 

#### 2.A: If you have sudo access. Preferred.
**NB**: It seems that compilation only works on Ubuntu 20.04+, As vulkan 1.2+ is needed and 18.04 only supports 1.1, but we haven't fully checked this...

- Upgrade `g++` and `gcc` to version 11
    ```bash
    sudo apt install build-essential manpages-dev software-properties-common
    sudo add-apt-repository ppa:ubuntu-toolchain-r/test
    sudo apt update && sudo apt install gcc-11 g++-11
    sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

    # verify
    g++ --version
    gcc --version
    ```
- CMake
    ```bash
    # if your system's cmake version is under 3.18, uninstall that and reinstall via snap
    sudo snap install cmake --classic
    ```
- CUDA, a system-wide CUDA 12.0+ is needed.
    - Download on https://developer.nvidia.com/cuda-12-1-0-download-archive
    - Install CUDA Toolkit.
    - Reboot.
    
    ```bash
    # verify
    nvcc --version
    ```
- Rust
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt-get install patchelf
    # if the above gives downloader error, make sure your curl was installed via apt, not snap
    ```
- Vulkan
    ```bash
    sudo apt install libvulkan-dev
    ```
- zlib
    ```bash
    sudo apt-get install zlib1g-dev
    ```
- RandR headers
    ```bash
    sudo apt-get install xorg-dev libglu1-mesa-dev
    ```
- libsnappy
    ```bash
    sudo apt-get install libsnappy-dev
    ```
- pybind
    ```bash
    pip install "pybind11[global]"
    ```
#### 2.B: If you have no sudo.
- conda dependencies
    ```bash
    conda install -c conda-forge gcc=11.4 gxx=11.4 cmake=3.26.1 minizip zlib libuuid patchelf vulkan-tools vulkan-headers
    ```
- rust
    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```
- pybind
    ```bash
    pip install "pybind11[global]"
    ```

### 3. Compile
- Build LuisaRender and its python binding:
    - If you used system dependencies (2.A)
        ```bash
        cd genesis/ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D LUISA_RENDER_BUILD_TESTS=OFF
        cmake --build build -j $(nproc)
        ```
        By default, we use OptiX denoiser (For CUDA backend only). If you need OIDN denoiser, append `-D LUISA_COMPUTE_DOWNLOAD_OIDN=ON`.
    - If you used conda dependencies (2.B)
        ```bash
        export CONDA_INCLUDE_PATH=path/to/anaconda/include
        cd ./ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D ZLIB_INCLUDE_DIR=$CONDA_INCLUDE_PATH
        cmake --build build -j $(nproc)
        ```
        The `CONDA_INCLUDE_PATH` typically looks like: `/home/user/anaconda3/envs/genesis/include`
        
### 4. FAQs
- Assertion 'lerror’ failed: Failed to write to the process: Broken pipe:
  You may need to use CUDA of the same version as compiled.
- if you followed 2.A and see "`GLIBCXX_3.4.30` not found"
    ```bash
    cd ~/anaconda3/envs/genesis/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```
### 5. GPU Rendering Troubleshooting (Silent Fallback to CPU)

Sometimes, when using `cam.render()` or viewer-related functions in Genesis, rendering becomes extremely slow.  
This is **not a Genesis issue**. Genesis relies on PyRender and EGL for GPU-based offscreen rendering. If your system isn’t correctly set up to use `libnvidia-egl`, it may **silently fall back to MESA (CPU) rendering**, severely affecting performance.

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
   echo '{
     "file_format_version" : "1.0.0",
     "ICD" : {
         "library_path" : "libEGL_nvidia.so.0"
     }
   }' | sudo tee /usr/share/glvnd/egl_vendor.d/10_nvidia.json
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

---

✅ **Summary**:  
Having both NVIDIA and MESA EGL libraries installed is sometimes okay — but if you're experiencing **silent fallback to CPU**, **remove MESA** and confirm that `libEGL_nvidia.so.0` is the only active one.

---
