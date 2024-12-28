# 🛠️ インストール方法
## 前提条件
* **Python**: 3.9以上
* **OS**: Linux (*推奨*) / MacOS / Windows

:::{note}
Genesisは***マルチプラットフォーム***に対応しており、*CPU*、*CUDA対応のGPU*、および*非CUDA GPU*を含むバックエンドデバイスをサポートしています。ただし、ベストな性能を得るためには、**Linux**プラットフォームと**CUDA対応GPU**の使用を推奨します。
:::

各システムでサポートされる機能は以下の通りです：
<div style="text-align: center;">

| OS  | GPUデバイス         | GPUシミュレーション | CPUシミュレーション | インタラクティブビューア | ヘッドレスレンダリング |
| ------- | ----------------- | ---------------- | ---------------- | -------------------- | ------------------ |
| Linux   | Nvidia            | ✅               | ✅               | ✅                   | ✅                 |
|         | AMD               | ✅               | ✅               | ✅                   | ✅                 |
|         | Intel             | ✅               | ✅               | ✅                   | ✅                 |
| Windows | Nvidia            | ✅               | ✅               | ❌                   | ❌                 |
|         | AMD               | ✅               | ✅               | ❌                   | ❌                 |
|         | Intel             | ✅               | ✅               | ❌                   | ❌                 |
| MacOS   | Apple Silicon     | ✅               | ✅               | ✅                   | ✅                 |

</div>

## インストール方法
1. GenesisはPyPI経由で利用可能です:
    ```bash
    pip install genesis-world
    ```

2. **PyTorch**を[公式手順](https://pytorch.org/get-started/locally/)に従ってインストールしてください。

## (オプション) モーションプランニング
GenesisはOMPLのモーションプランニング機能を統合しており、直感的なAPIを使用して簡単にモーションプランニングを実施できます。組み込みのモーションプランニング機能が必要な場合は、[ここ](https://github.com/ompl/ompl/releases/tag/prerelease)から事前コンパイル済みのOMPLのWheelをダウンロードし、`pip install`でインストールしてください。

## (オプション) サーフェス再構築
粒子ベースのエンティティ（流体、変形体など）を視覚化するためのメッシュ表面を再構築する必要がある場合、以下の2つのオプションをご用意しています：

1. [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf):
    最先端のサーフェス再構築法を使用して視覚化を実現します。
    ```bash
    cargo install splashsurf
    ```
2. ParticleMesher:
    OpenVDBをベースにした独自のサーフェス再構築ツール（高速だが滑らかさは劣る）。
    ```bash
    echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
    source ~/.bashrc
    ```

## (オプション) レイトレーシングレンダラー

写真のようにリアルなビジュアルを目指す場合、Genesisには[LuisaCompute](https://github.com/LuisaGroup/LuisaCompute)を使用したレイトレーシング（パストレーシング）ベースのレンダラーが組み込まれています。

### 1. LuisaRenderを取得
LuisaRenderは`ext/LuisaRender`サブモジュール内にあります：
```
git submodule update --init --recursive
```

### 2. 依存関係 

#### 2.A: 管理者権限がある場合（推奨）
**注意**: コンパイルはUbuntu 20.04以降でのみ動作するようです。Vulkan 1.2+が必要であり、18.04は1.1までしかサポートしていませんが、完全には確認していません。

- `g++` と `gcc` のバージョンを11にアップグレード
    ```
    sudo apt install build-essential manpages-dev software-properties-common
    sudo add-apt-repository ppa:ubuntu-toolchain-r/test
    sudo apt update && sudo apt install gcc-11 g++-11
    sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

    # バージョン確認
    g++ --version
    gcc --version
    ```
- cmakeをインストール
    ```
    # システムのcmakeバージョンが3.18未満の場合、卸してsnap経由で再インストール
    sudo snap install cmake --classic
    ```
- CUDAをインストール
    - システム全体で使用するCUDA（バージョン12.0以上）：
        - https://developer.nvidia.com/cuda-11-7-0-download-archive からダウンロード
        - CUDAツールキットをインストール
        - 再起動
- rustをインストール
    ```
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    sudo apt-get install patchelf
    # 上記でエラーが発生する場合、curlがaptからインストールされていることを確認
    ```
- Vulkanをインストール
    ```
    sudo apt install libvulkan-dev
    ```
- zlibをインストール
    ```
    sudo apt-get install zlib1g-dev
    ```
- RandRヘッダーをインストール
    ```
    sudo apt-get install xorg-dev libglu1-mesa-dev
    ```
- pybindをインストール
    ```
    pip install "pybind11[global]"
    ```
- libsnappyをインストール
    ```
    sudo apt-get install libsnappy-dev
    ```
#### 2.B: 管理者権限がない場合

- conda依存関係をインストール
    ```
    conda install -c conda-forge gcc=11.4 gxx=11.4 cmake=3.26.1 minizip zlib libuuid patchelf vulkan-tools vulkan-headers
    ```
- rustをインストール
    ```
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    ```
- pybindをインストール
    ```
    pip install "pybind11[global]"
    ```

### 3. コンパイル
- LuisaRenderとそのPythonバインディングをビルドする:
    - システム依存関係を使用した場合（2.A）
        ```
        cd genesis/ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF 
        cmake --build build -j $(nproc)
        ```
        デフォルトではOptiXデノイザを使用しています。OIDNが必要な場合、`-D LUISA_COMPUTE_DOWNLOAD_OIDN=ON`を追加。
    - conda依存関係を使用した場合（2.B）
        ```
        export CONDA_INCLUDE_PATH=path/to/anaconda/include
        cd ./ext/LuisaRender
        cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON -D LUISA_COMPUTE_ENABLE_GUI=OFF -D ZLIB_INCLUDE_DIR=$CONDA_INCLUDE_PATH
        cmake --build build -j $(nproc)
        ```
        `CONDA_INCLUDE_PATH`は典型的には`/home/user/anaconda3/envs/genesis/include`のようになります。

### 4. FAQ
- アサーションエラー 'lerror’ failed: Broken pipe:
  CUDAのバージョンがコンパイル時と一致しているか確認してください。
- 2.Aを使用している場合に"`GLIBCXX_3.4.30`が見つかりません"というエラー
    ```
    cd ~/anaconda3/envs/genesis/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```