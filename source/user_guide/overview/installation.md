# 🛠️ 安装

## 先决条件

* **Python**: 3.9+
* **操作系统**: Linux (推荐) / MacOS / Windows

:::{note}
Genesis 是跨平台的，支持 CPU、CUDA GPU 和非 CUDA GPU 设备。建议用带 CUDA GPU 的 Linux 系统以获得最佳性能。
:::

各系统支持的功能如下：

| 操作系统  | GPU 设备        | GPU 仿真 | CPU 仿真 | 交互式查看器 | 无头渲染 |
|:--------:|:----------------:|:--------:|:--------:|:------------:|:--------:|
| Linux   | Nvidia            | ✅       | ✅       | ✅           | ✅       |
|         | AMD               | ✅       | ✅       | ✅           | ✅       |
|         | Intel             | ✅       | ✅       | ✅           | ✅       |
| Windows | Nvidia            | ✅       | ✅       | ❌           | ❌       |
|         | AMD               | ✅       | ✅       | ❌           | ❌       |
|         | Intel             | ✅       | ✅       | ❌           | ❌       |
| MacOS   | Apple Silicon     | ✅       | ✅       | ✅           | ✅       |

## 基本安装

1. 根据[官方文档](https://pytorch.org/get-started/locally/)安装 PyTorch

2. 用 pip 安装 Genesis:

    ```bash
    pip install genesis-world
    ```

## 可选功能

### 1. 运动规划

Genesis 封装了 OMPL 的运动规划功能，提供简单易用的 API。如需使用，从[这里](https://github.com/ompl/ompl/releases/tag/prerelease)下载 OMPL wheel 并用 pip 安装。

### 2. 表面重建

如果要可视化粒子（流体、可变形物体等），需要把粒子重建成网格表面。有两种选择:

1. [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf) - 效果最好的表面重建工具:

    ```bash
    cargo install splashsurf
    ```

2. ParticleMesher - 我们基于 openVDB 开发的工具(速度快但效果一般):

    ```bash
    echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
    source ~/.bashrc
    ```

### 3. 光线追踪渲染器

Genesis 内置了基于 [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute) 的光线追踪渲染器。

#### 3.1 获取代码

拉取 LuisaRender 子模块:

```bash
git submodule update --init --recursive
```

#### 3.2 安装依赖

##### 方案A: 有 sudo 权限(推荐)

需要 Ubuntu 20.04+ (因为需要 Vulkan 1.2+)

* 安装 gcc-11:

    ```bash
    sudo apt install build-essential software-properties-common
    sudo add-apt-repository ppa:ubuntu-toolchain-r/test
    sudo apt update && sudo apt install gcc-11 g++-11
    sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110
    ```

* 安装其他依赖:

    ```bash
    sudo snap install cmake --classic
    sudo apt install libvulkan-dev zlib1g-dev xorg-dev libglu1-mesa-dev libsnappy-dev
    pip install "pybind11[global]"
    ```

* 安装 CUDA 12.0+: https://developer.nvidia.com/cuda-12-1-0-download-archive

* 安装 Rust:

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt install patchelf
    ```

##### 方案B: 无 sudo 权限

* 用 conda 安装依赖:

    ```bash
    conda install -c conda-forge gcc=11.4 gxx=11.4 cmake=3.26.1 minizip zlib libuuid patchelf vulkan-tools vulkan-headers
    pip install "pybind11[global]"
    ```

* 安装 Rust:

    ```bash
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```

#### 3.3 编译

* 方案A (系统依赖):

    ```bash
    cd genesis/ext/LuisaRender
    cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF 
    cmake --build build -j $(nproc)
    ```

* 方案B (conda 依赖):

    ```bash
    export CONDA_INCLUDE_PATH=/path/to/anaconda/include 
    cd ./ext/LuisaRender
    cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D ZLIB_INCLUDE_DIR=$CONDA_INCLUDE_PATH
    cmake --build build -j $(nproc)
    ```

#### 3.4 常见问题

* 断言 'lerror' 失败: 需要使用编译时的 CUDA 版本

* 如果用方案A遇到 "GLIBCXX_3.4.30 not found":

    ```bash
    cd ~/anaconda3/envs/genesis/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```
