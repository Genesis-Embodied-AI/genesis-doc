# 🚀 並列シミュレーション

```{figure} ../../_static/images/parallel_sim.png
```

GPUを使用してシミュレーションを高速化する最大の利点は、シーンレベルの並列化を可能にし、数千もの環境でロボットを同時にトレーニングできることです。

Genesisでは、並列シミュレーションを作成するのは想像以上に簡単です。シーンを構築するとき、「`n_envs`」という追加のパラメータを渡して、必要な環境数をシミュレータに伝えるだけです。それだけです。

文献での名前の命名規則に倣って、並列化操作を表すために「`batching`」という用語を使用することもあります。

### スクリプト例:
```python
import genesis as gs
import torch

########################## init ##########################
gs.init(backend=gs.gpu)

########################## create a scene ##########################
scene = gs.Scene(
    show_viewer    = True,
    viewer_options = gs.options.ViewerOptions(
        camera_pos    = (3.5, -1.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
    ),
    rigid_options = gs.options.RigidOptions(
        dt                = 0.01,
    ),
)

########################## entities ##########################
plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

########################## build ##########################

# 20の並列環境を作成
B = 20
scene.build(n_envs=B, env_spacing=(1.0, 1.0))

# すべてのロボットを制御
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 0, 0, 0.02, 0.02], device=gs.device), (B, 1)
    ),
)

for i in range(1000):
    scene.step()
```

上記のスクリプトは、[Hello, Genesis](hello_genesis.md) の例とほぼ同じですが、`scene.build()` が次の2つの追加パラメータで拡張されています:
- `n_envs`: 作成するバッチ化された環境の数を指定します。
- `env_spacing`: 生成された並列環境は同一の状態を共有します。可視化の目的で、このパラメータを指定することで、すべての環境を各環境間の距離を (x, y) メートルで指定されたグリッドに分配するようビジュアライザに指示できます。なお、これは可視化動作のみに影響し、各環境内のエンティティの実際の位置には影響を与えません。

---

### バッチ化された環境でのロボット制御
以前のチュートリアルで `franka.control_dofs_position()` のようなAPIを使用したことを思い出してください。同じAPIをそのまま使用してバッチ化されたロボットを制御できます。ただし、入力変数に追加のバッチ次元を持たせる必要があります:
```python
franka.control_dofs_position(torch.zeros(B, 9, device=gs.device))
```
GPU上でシミュレーションを実行するため、CPUとGPU間のデータ転送オーバーヘッドを削減する目的で、Numpy配列ではなく `gs.device` を使用して選択したTorchテンソルを使用することを推奨します（ただしNumpy配列も使用可能です）。特に大きなバッチサイズのテンソルを頻繁に送信する場合、これにより顕著なパフォーマンス向上が得られることがあります。

上記の呼び出しは、バッチ化された環境内のすべてのロボットを制御します。一部の環境のみを制御したい場合は、`envs_idx` を追加で渡します。ただし、`position` テンソルのバッチ次元のサイズが `envs_idx` の長さと一致していることを確認してください:
```python
# 環境1、5、および7のみを制御
franka.control_dofs_position(
    position = torch.zeros(3, 9, device=gs.device),
    envs_idx = torch.tensor([1, 5, 7], device=gs.device),
)
```
この呼び出しは、選択された3つの環境にゼロ位置コマンドを送信します。

---

### 未来のスピードを堪能しよう！
Genesisは最大数万もの並列環境をサポートしており、かつてないシミュレーション速度を実現します。では、ビューワーをオフにし、バッチサイズを30000に変更してみましょう（GPUのVRAMが相対的に小さい場合は、より小さい値を検討してください）。

```python
import torch
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(
    show_viewer   = False,
    rigid_options = gs.options.RigidOptions(
        dt                = 0.01,
    ),
)

plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file='xml/franka_emika_panda/panda.xml'),
)

scene.build(n_envs=30000)

# すべてのロボットを制御
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 0, 0, 0.02, 0.02], device=gs.device), (30000, 1)
    ),
)

for i in range(1000):
    scene.step()
```

上記のスクリプトを、RTX 4090と14900Kを搭載したデスクトップで実行すると、未来的なシミュレーション速度が楽しめます -- **毎秒4300万フレーム以上**を実現します。これはリアルタイムの430,000倍です。お楽しみください！

```{figure} ../../_static/images/parallel_speed.png
```

:::{tip}
**FPS ロギング:** デフォルトでは、Genesisのロガーは端末にリアルタイムのシミュレーション速度を表示します。この動作は、シーン作成時に `show_FPS=False` を設定することで無効にできます。
:::