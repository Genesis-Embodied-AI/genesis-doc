# 📸 ビジュアライゼーションとレンダリング

Genesisのビジュアライゼーションシステムは、作成したシーンの`visualizer`（例えば、`scene.visualizer`）によって管理されます。シーンを視覚化する方法は2つあります。1）別スレッドで動作するインタラクティブビューアを使用する方法、2）シーンにカメラを手動で追加し、それを使って画像をレンダリングする方法です。


## ビューア
ディスプレイに接続されている場合、インタラクティブビューアを使用してシーンを視覚化できます。Genesisは、シーン内のさまざまなコンポーネントを構成するために異なる`options`グループを使用します。ビューアを構成するには、シーンを作成するときに`viewer_options`のパラメーターを変更できます。さらに、`vis_options`を使用して視覚化に関連するプロパティを指定します。これらのプロパティは、ビューアとカメラ（後ほど追加する）で共有されます。

より詳細なビューア設定と視覚化設定を使用してシーンを作成します（少し複雑に見えますが、これは説明用の例です）:
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
        show_world_frame = True, # `world`の原点座標系を可視化
        world_frame_size = 1.0, # 座標系の長さ（メートル単位）
        show_link_frame  = False, # エンティティリンクの座標系は非表示
        show_cameras     = False, # 追加されたカメラのメッシュと視錐台を非表示
        plane_reflection = True, # 平面反射を有効化
        ambient_light    = (0.1, 0.1, 0.1), # 環境光設定
    ),
    renderer = gs.renderers.Rasterizer(), # カメラレンダリングにラスタライザを使用
)
```
ここでは、ビューアカメラのポーズとFOVを指定できます。`max_FPS`が`None`に設定されている場合、ビューアは可能な限り高速で動作します。`res`が`None`の場合、Genesisは表示画面の高さの半分を設定にした4:3のウィンドウを自動的に作成します。また、上記の設定では、カメラレンダリングにラスタライザバックエンドを使用するように設定されています。Genesisは、`gs.renderers.Rasterizer()`（ラスタライザ）と`gs.renderers.RayTracer()`（レイトレーサ）の2つのレンダリングバックエンドを提供します。ビューアは常にラスタライザを使用します。デフォルトでは、カメラもラスタライザを使用します。

シーンが作成されると、`scene.visualizer.viewer`またはショートカットである単純な`scene.viewer`を使用してビューアオブジェクトにアクセスできます。ビューアカメラのポーズをクエリしたり設定したりすることができます:
```python
cam_pose = scene.viewer.camera_pose

scene.viewer.set_camera_pose(cam_pose)
```

## カメラとヘッドレスレンダリング
次に、シーンにカメラオブジェクトを手動で追加してみましょう。カメラはビューアやディスプレイに接続されず、必要に応じてレンダリングされた画像を返します。そのため、カメラはヘッドレスモードで動作します。

```python
cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)
```
`GUI=True`にすると、各カメラでレンダリングされた画像を動的に表示するOpenCVウィンドウが作成されます。これはビューアのGUIとは異なる点に注意してください。

次に、シーンをビルドした後、カメラを使って画像をレンダリングできます。カメラは、RGB画像、深度、セグメンテーションマスク、表面法線をレンダリングできます。デフォルトではRGBのみがレンダリングされ、他のモードは`camera.render()`を呼び出す際にパラメータを設定することで有効化できます。

```python
scene.build()

# RGB、深度、セグメンテーションマスク、法線マップをレンダリング
rgb, depth, segmentation, normal = cam.render(depth=True, segmentation=True, normal=True)
```

`GUI=True`を使用し、ディスプレイが接続されている場合、4つのウィンドウを確認できるはずです。（時々OpenCVウィンドウに遅延が発生する場合があるため、画面が真っ黒な場合は`cv2.waitKey(1)`を追加で呼び出すか、単純にもう一度`render()`を呼び出してウィンドウを更新してください。）

```{figure} ../../_static/images/multimodal.png
```

**カメラを使用してビデオを録画する**

次に、RGB画像だけをレンダリングし、カメラを移動させながらビデオを録画してみましょう。Genesisはビデオ録画のための便利なユーティリティを提供しています:
```python
# カメラ録画を開始します。開始後、レンダリングされたすべてのRGB画像は内部的に録画されます。
cam.start_recording()

import numpy as np
for i in range(120):
    scene.step()

    # カメラの位置を変更
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    
    cam.render()

# 録画を停止してビデオを保存します。`filename`を指定しない場合、呼び出し元のファイル名を使用して名前が自動生成されます。
cam.stop_recording(save_to_filename='video.mp4', fps=60)
```
これでビデオが`video.mp4`として保存されます:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/cam_record.mp4" type="video/mp4">
</video>

以下は、上記で説明した内容をカバーする完全なコードスクリプトです:
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
        show_world_frame = True, # ワールド座標系のフレームを表示
        world_frame_size = 1.0, # ワールドフレームの長さを1.0メートルに設定
        show_link_frame  = False, # リンクフレームは非表示
        show_cameras     = False, # カメラのメッシュと視錐体は非表示
        plane_reflection = True, # 平面反射を有効化
        ambient_light    = (0.1, 0.1, 0.1), # 環境光を設定
    ),
    renderer=gs.renderers.Rasterizer(), # ラスタライザを使用
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

# RGB、深度、セグメンテーションマスク、法線をレンダリング
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

## フォトリアリスティックなレイトレーシングレンダリング

Genesisは、フォトリアルなレンダリングのためのレイトレーシングレンダリングバックエンドを提供しています。このバックエンドを使用するには、シーン作成時に`renderer=gs.renderers.RayTracer()`を設定するだけです。このカメラでは、`spp`、`aperture`、`model`など、より多くのパラメータ調整が可能です。

### セットアップ

動作確認環境:
- Ubuntu 22.04、CUDA 12.4、Python 3.9

サブモジュールを取得します（特に`genesis/ext/LuisaRender`）。
```bash
# Genesis/ディレクトリ内
git submodule update --init --recursive
pip install -e ".[render]"
```
g++ と gcc をバージョン 11 にインストール/アップグレード
```bash
sudo apt install build-essential manpages-dev software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update && sudo apt install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 110
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 110

# バージョン確認
g++ --version
gcc --version
```

### cmake をインストール
apt ではなく snap を使用する理由は、バージョンが 3.26 以上必要だからです。しかし、正しい cmake を使用することを忘れないでください。たとえば、`/usr/local/bin/cmake` があっても、snap でインストールしたパッケージは `/snap/bin/cmake`（または `/usr/bin/snap`）にあります。`echo $PATH` を使用してバイナリパスの順序を確認してください。
```bash
sudo snap install cmake --classic
cmake --version
```

### 依存関係をインストール
```bash
sudo apt install libvulkan-dev # Vulkan
sudo apt-get install zlib1g-dev # zlib
sudo apt-get install libx11-dev # X11
sudo apt-get install xorg-dev libglu1-mesa-dev # RandR ヘッダー
```

### `LuisaRender` をビルド
正しい cmake を使用することを忘れないでください。
```bash
cd genesis/ext/LuisaRender
cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON # Python のバージョンを確認
cmake --build build -j $(nproc)
```

もしビルドがどうしてもうまくいかない場合、いくつかのビルド済みファイルを[こちら](https://drive.google.com/drive/folders/1Ah580EIylJJ0v2vGOeSBU_b8zPDWESxS?usp=sharing)に用意しているので、マシンのセットアップが一致しているか確認できます。命名は `build_<commit-tag>_cuda<version>_python<version>` の形式になっています。一致するものをダウンロードして `build/` にリネームし、`genesis/ext/LuisaRender` に配置してください。

### 最後に例を実行
```bash
cd examples/rendering
python demo.py
```

次のような出力が得られるはずです。
```{figure} ../../_static/images/raytracing_demo.png
```


### よくある質問（FAQ）

- `cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON` を実行した際の Pybind エラー
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
    → おそらく `pip install -e ".[render]"` を忘れています。代わりに、単に `pip install "pybind11[global]"` を実行することもできます。

- `cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON` を実行した際の CUDA ランタイムコンパイルエラー
    ```bash
    /usr/bin/ld: CMakeFiles/luisa-cuda-nvrtc-standalone-compiler.dir/cuda_nvrtc_compiler.cpp.o: in function `main':
    cuda_nvrtc_compiler.cpp:(.text.startup+0x173): undefined reference to `nvrtcGetOptiXIRSize'
    /usr/bin/ld: cuda_nvrtc_compiler.cpp:(.text.startup+0x197): undefined reference to `nvrtcGetOptiXIR'
    ```
    → システムレベルで CUDA ツールキットをインストールする必要があります（[公式インストールガイド](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)参照）。まず CUDA ツールキットを確認してください。
    ```bash
    nvcc --version # これは nvidia-smi で確認した CUDA バージョンと一致するはず
    which nvcc # 期待している CUDA ツールキットを使用しているか確認
    ```

    `nvcc` が正しい出力を返さない場合、公式ガイドに従って CUDA ツールキットをインストールしてください。以下は CUDA 12.4 をインストールする例です。[こちら](https://developer.nvidia.com/cuda-12-4-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local)からインストーラーをダウンロードします。
    ```bash
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2204-12-4-local_12.4.0-550.54.14-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2204-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get -y install cuda-toolkit-12-4
    ```

    バイナリとランタイムライブラリのパスを設定するのを忘れないでください。`~/.bashrc`に以下を追加します（なお、CUDA のパスは最後尾に追加しています。理由は `/usr/local/cuda-12.4/bin` に別バージョンの `gcc` や `g++` が含まれており、バージョン 11 がビルドに必要なためです）。
    ```bash
    PATH=${PATH:+${PATH}:}/usr/local/cuda-12.4/bin
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```

    ターミナルを再起動するか `source ~/.bashrc` を実行してください。

    別のエラーとして次のようなものが出る場合があります。
    ```bash
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_fatal_printf@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_symbind_alt@GLIBC_PRIVATE'
    <your-env-path>/genesis-test1/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_exception_create@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__nptl_change_stack_perm@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `__tunable_get_val@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_audit_preinit@GLIBC_PRIVATE'
    <your-env-path>/bin/ld: /lib/x86_64-linux-gnu/libc.so.6: undefined reference to `_dl_find_dso_for_object@GLIBC_PRIVATE'
    ```

    これは、conda 環境内の CUDA ツールキットが原因かもしれません。以下を実行してシステムレベルの CUDA をインストールしてください。
    ```bash
    which nvcc
    conda uninstall cuda-toolkit
    ```

    もしくは、conda のライブラリパスをランタイムライブラリパスに追加することで解消できます。
    ```bash
    ls $CONDA_PREFIX/lib/libcudart.so # このファイルが存在するか確認

    # ~/.bashrc 内に追加
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}/usr/local/cuda-12.4/lib64
    ```

    上記の修正を行った後はビルドディレクトリをクリアしてください。
    ```bash
    rm -r build
    ```

- `cmake -S . -B build -D CMAKE_BUILD_TYPE=Release -D PYTHON_VERSIONS=3.9 -D LUISA_COMPUTE_DOWNLOAD_NVCOMP=ON` を実行した際のコンパイラーエラー
    ```bash
    CMake Error at /snap/cmake/1435/share/cmake-3.31/Modules/CMakeDetermineCCompiler.cmake:49 (message):
    Could not find compiler set in environment variable CC:

    /home/tsunw/miniconda3/envs/genesis-test1/bin/x86_64-conda-linux-gnu-cc.
    Call Stack (most recent call first):
    CMakeLists.txt:21 (project)


    CMake Error: CMAKE_C_COMPILER not set, after EnableLanguage
    CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
    ```

    → `gcc` と `g++` のバージョン 11 を使用していない可能性があります。以下を確認してください。
    ```bash
    gcc --version
    g++ --version
    which gcc
    which g++
    echo $PATH # 例: /usr/local/cuda-12.4/bin/gcc (バージョン 10.5) が /usr/bin/gcc (バージョン 11) より優先されないようにする
    ```

- `examples/rendering/demo.py` を実行した際の ImportError:
    ```bash
    [Genesis] [11:29:47] [ERROR] Failed to import LuisaRenderer. ImportError: /home/tsunw/miniconda3/envs/genesis-test1/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.30' not found (required by /home/tsunw/workspace/Genesis/genesis/ext/LuisaRender/build/bin/liblc-core.so)
    ```

    Conda の `libstdc++.so.6` が 3.4.30 をサポートしていません。以下のようにしてシステムのものを Conda に適用してください（[参考](https://stackoverflow.com/a/73708979)）。
    ```bash
    cd $CONDA_PREFIX/lib
    mv libstdc++.so.6 libstdc++.so.6.old
    ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 libstdc++.so.6
    ```
