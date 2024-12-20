# 🛠️ 安装

## 先决条件

* **Python**: 3.9+
* **操作系统**: Linux (*推荐*) / MacOS / Windows

:::{note}
Genesis 设计为***跨平台***，支持包括 *CPU*、*CUDA GPU* 和 *非CUDA GPU* 在内的后端设备。尽管如此，推荐使用带有 **CUDA 兼容 GPU** 的 **Linux** 平台以获得最佳性能。
:::

各系统支持的功能如下：
<div style="text-align: center;">

| 操作系统  | GPU 设备        | GPU 仿真 | CPU 仿真 | 交互式查看器 | 无头渲染 |
| ------- | ----------------- | -------- | -------- | ------------ | -------- |
| Linux   | Nvidia            | ✅       | ✅       | ✅           | ✅       |
|         | AMD               | ✅       | ✅       | ✅           | ✅       |
|         | Intel             | ✅       | ✅       | ✅           | ✅       |
| Windows | Nvidia            | ✅       | ✅       | ❌           | ❌       |
|         | AMD               | ✅       | ✅       | ❌           | ❌       |
|         | Intel             | ✅       | ✅       | ❌           | ❌       |
| MacOS   | Apple Silicon     | ✅       | ✅       | ✅           | ✅       |

</div>

## 安装

1. Genesis 可以通过 PyPI 获取：

    ```bash
    pip install genesis-world
    ```

2. 按照[官方说明](https://pytorch.org/get-started/locally/)安装 **PyTorch**。

## （可选）运动规划

Genesis 集成了 OMPL 的运动规划功能，并使用直观的 API 封装以实现轻松的运动规划。如果需要内置的运动规划功能，请从[这里](https://github.com/ompl/ompl/releases/tag/prerelease)下载预编译的 OMPL wheel，然后使用 `pip install` 安装。

## （可选）表面重建

如果需要可视化粒子实体（流体、可变形物体等）的精美视觉效果，通常需要使用内部的基于粒子的表示来重建网格表面。我们提供了以下两种选择：

1. [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf)，一种最先进的表面重建方法：

    ```bash
    cargo install splashsurf
    ```

2. ParticleMesher，我们基于 openVDB 的表面重建工具（速度更快但不如前者平滑）：

    ```bash
    echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
    source ~/.bashrc
    ```

## （可选）光线追踪渲染器

如果需要照片级真实感的视觉效果，Genesis 内置了一个基于光线追踪（路径追踪）的渲染器，使用 [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute) 开发，这是一个为渲染设计的高性能领域特定语言。

### 1. 获取 LuisaRender

子模块 LuisaRender 位于 `ext/LuisaRender`：

```
git submodule update --init --recursive
```

### 2. 依赖项

#### 2.A: 如果有 sudo 权限。优选

**注意**：编译似乎仅在 Ubuntu 20.04+ 上有效，因为需要 Vulkan 1.2+，而 18.04 仅支持 1.1，但我尚未完全验证...

* 升级 `g++` 和 `gcc` 到版本 11

    ```
    sudo apt install build-essential manpages-dev software-properties-common
    sudo add-apt-repository ppa:ubuntu-toolchain-r/test
    sudo apt update && sudo apt install gcc-11 g++-11
    sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

    # 验证
    g++ --version
    gcc --version
    ```

* cmake

    ```
    # 如果系统的 cmake 版本低于 3.18，卸载并通过 snap 重新安装
    sudo snap install cmake --classic
    ```

* CUDA
  * 需要安装系统范围的 CUDA（现在是 12.0+）。
    * 下载 <https://developer.nvidia.com/cuda-11-7-0-download-archive>
    * 安装 CUDA 工具包。
    * 重启

* rust

    ```
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt-get install patchelf
    # 如果上面的命令出现下载错误，请确保 curl 是通过 apt 安装的，而不是 snap
    ```

* Vulkan

    ```
    sudo apt install libvulkan-dev
    ```

* zlib

    ```
    sudo apt-get install zlib1g-dev
    ```

* RandR 头文件

    ```
    sudo apt-get install xorg-dev libglu1-mesa-dev
    ```

* pybind

    ```
    pip install "pybind11[global]"
    ```

* libsnappy

    ```
    sudo apt-get install libsnappy-dev
    ```

#### 2.B: 如果没有 sudo 权限

* conda 依赖项

    ```
    conda install -c conda-forge gcc=11.4 gxx=11.4 cmake=3.26.1 minizip zlib libuuid patchelf vulkan-tools vulkan-headers
    ```

* rust

    ```
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

* pybind

    ```
    pip install "pybind11[global]"
    ```

### 3. 编译

* 构建 LuisaRender 及其 Python 绑定：
  * 如果使用系统依赖项（2.A）

        ```
        cd genesis/ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF 
        cmake --build build -j $(nproc)
        ```

        默认情况下，我们使用 optix 去噪器。如果需要 OIDN，请添加 `-D LUISA_COMPUTE_DOWNLOAD_OIDN=ON`。
  * 如果使用 conda 依赖项（2.B）

        ```
        export CONDA_INCLUDE_PATH=path/to/anaconda/include
        cd ./ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D ZLIB_INCLUDE_DIR=$CONDA_INCLUDE_PATH
        cmake --build build -j $(nproc)
        ```

        `CONDA_INCLUDE_PATH` 通常类似于：`/home/user/anaconda3/envs/genesis/include`

### 4. 常见问题

* 断言 'lerror’ 失败：写入进程失败：管道破裂：
  可能需要使用与编译时相同版本的 CUDA。

* 如果按照 2.A 操作并看到 "`GLIBCXX_3.4.30` not found"

    ```
    cd ~/anaconda3/envs/genesis/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```

