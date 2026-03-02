# 🛠️ インストール
## 前提条件
* **Python**: >=3.10,<3.14
* **OS**: Linux（**推奨**）/ MacOS / Windows

:::{note}
Genesis は ***クロスプラットフォーム*** 設計で、*CPU*、*CUDA GPU*、*non-CUDA GPU* の各バックエンドに対応しています。
ただし最良の性能を得るため、**Linux** + **CUDA 対応 GPU** の利用を推奨します。
:::

各システムでサポートされる機能は次のとおりです。
<div style="text-align: center;">

| OS  | GPU デバイス        | GPU シミュレーション | CPU シミュレーション | インタラクティブビューア | ヘッドレスレンダリング |
| ------- | ----------------- | -------------- | -------------- | ---------------- | ------------------ |
| Linux   | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| Windows | Nvidia            | ✅             | ✅             | ✅               | ✅                 |
|         | AMD               | ✅             | ✅             | ✅               | ✅                 |
|         | Intel             | ✅             | ✅             | ✅               | ✅                 |
| MacOS   | Apple Silicon     | ✅             | ✅             | ✅               | ✅                 |

</div>

## インストール
1. [公式手順](https://pytorch.org/get-started/locally/) に従って **PyTorch** をインストールします。

2. PyPI から Genesis をインストールします。
    ```bash
    pip install genesis-world
    ```

:::{note}
CUDA で Genesis を使う場合、適切な nvidia-driver がインストールされていることを確認してください。
:::

## （オプション）サーフェス再構成

粒子ベースエンティティ（流体・変形体など）を高品質に可視化したい場合、内部の粒子表現からメッシュ表面を再構成する必要があることがあります。
この用途に、最先端の再構成ツール [splashsurf](https://github.com/InteractiveComputerGraphics/splashsurf) をそのまま利用できます。
また、より高速だが品質は低めの openVDB ベース自前実装 `ParticleMesher` も提供しています。
```bash
echo "export LD_LIBRARY_PATH=${PWD}/ext/ParticleMesher/ParticleMesherPy:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc
```

## （オプション）レイトレーシングレンダラー

フォトリアルな描画が必要な場合、Genesis には [LuisaCompute](https://github.com/LuisaGroup/LuisaCompute) で実装されたパストレーシング型レンダラーが内蔵されています。
設定方法は [ビジュアライゼーションとレンダリング](../getting_started/visualization.md) を参照してください。

## （オプション）USD アセット

USD アセットを Genesis シーンへ読み込みたい場合は、[USD 読み込み設定](../getting_started/usd_import.md#installation) の手順を参照してください。

## トラブルシューティング

### インポートエラー

#### 「Genesis が初期化されていません（Genesis hasn't been initialized）」 

Genesis が初期化されていない状態でエンジン関連サブモジュールを import すると、次のような例外が発生します。
```python
Traceback (most recent call last):
  File "/home/jeremy/Downloads/Genesis_Jeremy/examples/./init_error.py", line 3, in <module>
    from genesis.engine.entities import RigidEntity
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/engine/entities/rigid_entity/rigid_entity.py", line 14, in <module>
    from genesis.utils import array_class
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/array_class.py", line 13, in <module>
    gs.raise_exception("Genesis hasn't been initialized. Did you call `gs.init()`?")
  File "/home/jeremy/.pyenv/versions/spider-genesis/lib/python3.11/site-packages/genesis/utils/misc.py", line 42, in raise_exception
    raise gs.GenesisException(msg)
genesis.GenesisException: Genesis hasn't been initialized. Did you call `gs.init()`?
```

これはバグではなく仕様です。
低レベル機能（高速キャッシュ機構や Quadrants の動的配列モードなど）を設定できるようにするため、エンジン関連サブモジュールは Genesis 初期化後に import する必要があります。
実運用ではエンジンクラスを直接インスタンス化することは通常ないため、ほとんどの場合問題になりません。
型チェック目的で import したい場合は、次のようにガードしてください。
```python
from typing import TYPE_CHECKING

import genesis as gs
if TYPE_CHECKING:
    from genesis.engine.entities.drone_entity import DroneEntity
```

#### 循環インポートエラー

現在ディレクトリが Genesis のソースディレクトリだと、Genesis の（循環）import に失敗する場合があります。
これは、PyPI またはソースから editable モードなしでインストールしているケースで起こりやすいです。
回避策は、Python 実行前にソースディレクトリから移動することです。
恒久対応としては editable インストールへ切り替えてください。
まず `genesis-world` をアンインストールし、Genesis ソースディレクトリ内で `pip install -e '.[render]'` を実行します。

### [Native Ubuntu] 描画が遅い（CPU へのソフトウェアフォールバック）

Genesis で `cam.render()` や viewer 関連機能を使うと極端に遅くなる場合があります。
これは **Genesis 側の問題ではありません**。
Genesis は GPU オフスクリーン描画のため PyRender と EGL を利用しますが、`libnvidia-egl` が正しく設定されていないと **MESA（CPU 描画）へ静かにフォールバック** し、性能が大きく低下します。

GPU が見えていても、明示設定しないと CPU 描画へ落ちるケースがあります。

---

#### ✅ GPU 描画を有効化する

1. **NVIDIA GL ライブラリをインストール**
   ```bash
   sudo apt update && sudo apt install -y libnvidia-gl-525
   ```

2. **EGL が NVIDIA ドライバを指しているか確認**
   ```bash
   ldconfig -p | grep EGL
   ```
   理想的には次が見えるはずです。
   ```
   libEGL_nvidia.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_nvidia.so.0
   ```

   ⚠️ 次が見える場合があります。
   ```
   libEGL_mesa.so.0 (libc6,x86-64) => /lib/x86_64-linux-gnu/libEGL_mesa.so.0
   ```

   これは必ずしも問題ではありませんが、**描画が遅い** 場合は Mesa 削除が有効なことがあります。

3. **（任意だが推奨）Mesa を削除してフォールバックを防ぐ**
   ```bash
   sudo apt remove -y libegl-mesa0 libegl1-mesa libglx-mesa0
   ```
   その後再確認:
   ```bash
   ldconfig -p | grep EGL
   ```
   ✅ `libEGL_nvidia.so.0` のみが見える状態が理想です。

4. **（任意・特殊ケース）NVIDIA EGL ICD 設定ファイルを確認**

    通常は NVIDIA ドライバが正しく入っていればこのファイルは存在します。
    ただし、最小構成環境やコンテナ環境（例: ヘッドレス Docker）では EGL 初期化失敗時に手動作成が必要な場合があります。
    ```bash
    cat /usr/share/glvnd/egl_vendor.d/10_nvidia.json
    ```
    内容は次のようになります。
    ```json
    {
        "file_format_version" : "1.0.0",
        "ICD" : {
            "library_path" : "libEGL_nvidia.so.0"
        }
    }
    ```

    なければ作成:
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

    同様に CUDA ランタイムのシンボリックリンクが不足している場合があります。
    ```bash
    ln -s /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/lib/x86_64-linux-gnu/libcuda.so
    ```

5. **グローバル環境変数を設定**

Genesis は通常 EGL 描画を自動で試みるため、多くの環境では `PYOPENGL_PLATFORM` 手動指定は不要です。
ただし Docker やヘッドレスサーバなどでは明示設定で安定する場合があります。

   `~/.bashrc` または `~/.zshrc` に追記:
   ```bash
   export NVIDIA_DRIVER_CAPABILITIES=all
   export PYOPENGL_PLATFORM=egl
   ```

   再読み込み:
   ```bash
   source ~/.bashrc  # or source ~/.zshrc
   ```

   確認:
   ```python
   import os
   print("[DEBUG] Using OpenGL platform:", os.environ.get("PYOPENGL_PLATFORM"))
   print("[DEBUG] NVIDIA capabilities:", os.environ.get("NVIDIA_DRIVER_CAPABILITIES"))
   ```

### [Windows 11 + WSL2 上の Genesis Docker] 画面が黒く表示される

    Nvidia GPU マシンでは NVIDIA Container Toolkit がインストールされていることを確認してください。公式ガイドは [こちら](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)。

    Windows 上で Genesis ベース Docker コンテナを実行した際に描画問題が残る場合、Linux の動的ライブラリ検索パス（`LD_LIBRARY_PATH`）へ WSL ライブラリを追加すると改善することがあります。
    ```bash
    docker run --gpus all --rm -it \
    -e DISPLAY=$DISPLAY \
    -e LD_LIBRARY_PATH=/usr/lib/wsl/lib \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    genesis
    ```

### [Windows 11 + WSL2 上の Ubuntu VM] OpenGL エラー

    Nvidia GPU マシンでは、Ubuntu VM 内で以下の環境変数を設定し GPU 描画を強制してみてください。
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    export GALLIUM_DRIVER=d3d12
    export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
    ```

    うまくいかない場合は OSMesa の最新版を試してください。
    ```bash
    sudo add-apt-repository ppa:kisak/kisak-mesa
    sudo apt update
    sudo apt upgrade
    ```
    その後は direct rendering（直接描画）のみ有効化:
    ```bash
    export LIBGL_ALWAYS_INDIRECT=0
    ```

    この時点で `glxinfo` を使い、既定 OpenGL ベンダーを確認できます。
    ```bash
    glxinfo -B
    ```

    最後の手段として、必要なら OSMesa による CPU 描画を強制します。
    ```bash
    export LIBGL_ALWAYS_SOFTWARE=1
    ```

### [Windows 11 + WSL2 上の Ubuntu VM] Quadrants/Genesis が `cudalib.so` を見つけられず CPU フォールバックする

PyTorch と Genesis を導入後、torch は CUDA を使えているのに Quadrants が CPU フォールバックする場合があります。

症状:

- `python -c "import torch; print(torch.zeros((3,), device='cuda'))"` は `tensor([0., 0., 0.], device='cuda:0')` を出力
- しかし `python -c "import quadrants as qd; qd.init(arch=qd.gpu)"` は次のような出力
    ```
    [W 06/18/25 12:47:56.784 14507] [cuda_driver.cpp:load_lib@36] libcuda.so lib not found.
    [Quadrants] Starting on arch=vulkan
    ```

対処:

- `ls /usr/lib/wsl/lib/` で libcuda.so などの CUDA ライブラリ存在を確認
- 存在する場合は `export LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH` を設定
