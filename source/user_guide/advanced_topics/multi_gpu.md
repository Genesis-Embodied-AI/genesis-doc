# 🖥️ マルチ GPU シミュレーション

Genesis は、シミュレーションのスケール拡張に向けたマルチ GPU 実行をサポートします。

## 単一 GPU 設定

```python
import genesis as gs

# 自動 GPU 選択
gs.init(backend=gs.gpu)

# バックエンドを明示指定
gs.init(backend=gs.cuda)   # NVIDIA CUDA
gs.init(backend=gs.metal)  # Apple Metal
gs.init(backend=gs.cpu)    # CPU フォールバック
```

## 並列環境（単一 GPU）

1 枚の GPU 上で環境をバッチ化してスケールします。

```python
scene.build(n_envs=2048, env_spacing=(1.0, 1.0))
# 全環境を同一 GPU 上で並列実行
```

## マルチプロセスによるマルチ GPU

GPU ごとに別プロセスを実行します。

```python
import os
import multiprocessing

def run_simulation(gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    os.environ["QD_VISIBLE_DEVICE"] = str(gpu_id)
    os.environ["EGL_DEVICE_ID"] = str(gpu_id)

    import genesis as gs
    gs.init(backend=gs.gpu)
    # ... シミュレーションコード ...

if __name__ == "__main__":
    for i in range(2):  # GPU 2 枚
        p = multiprocessing.Process(target=run_simulation, args=(i,))
        p.start()
```

## 分散学習（DDP）

PyTorch Distributed Data Parallel を使用します。

```bash
torchrun --standalone --nnodes=1 --nproc_per_node=2 train.py
```

```python
import os
import torch
import torch.distributed as dist
import genesis as gs

local_rank = int(os.environ.get("LOCAL_RANK", 0))
os.environ["CUDA_VISIBLE_DEVICES"] = str(local_rank)
os.environ["QD_VISIBLE_DEVICE"] = str(local_rank)

gs.init(backend=gs.gpu, seed=local_rank)
scene.build(n_envs=2048)

torch.cuda.set_device(0)
dist.init_process_group(backend="nccl", init_method="env://")
model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[0])

# 勾配同期ありの学習ループ
for step in range(steps):
    scene.step()
    loss.backward()  # DDP が all-reduce を処理
    optimizer.step()

dist.barrier()
dist.destroy_process_group()
```

## 環境変数

| 変数 | 用途 |
|----------|---------|
| `CUDA_VISIBLE_DEVICES` | PyTorch/CUDA の GPU 選択 |
| `QD_VISIBLE_DEVICE` | Quadrants の GPU 選択 |
| `EGL_DEVICE_ID` | レンダリング GPU（OpenGL/EGL） |

マルチ GPU 構成では、必ず 3 つを揃えて設定してください。

## GPU 選択パターン

| パターン | 方法 | GPU 数 | 複雑さ |
|---------|--------|------|------------|
| 単一 GPU | `gs.init(backend=gs.gpu)` | 1 | 低 |
| バッチ環境 | `scene.build(n_envs=N)` | 1 | 低 |
| マルチプロセス | Multiprocessing + 環境変数 | N | 中 |
| 分散実行 | `torchrun` + DDP | N | 高 |

## ベストプラクティス

1. **まずバッチ化**: いきなりマルチ GPU にせず、単一 GPU で大きな `n_envs` を試す
2. **環境変数を全設定**: CUDA / Quadrants / EGL を常にセットで指定する
3. **DDP 同期**: プロセスグループ破棄前に `dist.barrier()` を呼ぶ
4. **ヘッドレス描画**: サーバでは `pyglet.options["headless"] = True` を設定
5. **メモリ監視**: バッチ実行中は `nvidia-smi` で確認

## デバイスアクセス

初期化後:

```python
gs.device    # PyTorch device (e.g., "cuda:0", "mps:0")
gs.backend   # Backend type (gs.cuda, gs.metal, gs.cpu)
```
