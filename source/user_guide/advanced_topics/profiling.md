# Genesis と Quadrants のプロファイリング

## Quadrants カーネル実行時間の計測と launch レイテンシ確認

例えば次のように、コードへ PyTorch profiler を追加します。

```python
    schedule=torch.profiler.schedule(
        wait=80,
        warmup=3,
        active=1,
        repeat=1
    )
    with torch.profiler.profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        schedule=schedule,
        record_shapes=False,
        profile_memory=False,
        with_stack=True,
        with_flops=False,
    ) as profiler:
        for _ in range(steps):
            profiler.step()
    # これは context manager の外側で呼ぶ必要があります
    profiler.export_chrome_trace("trace.json")
```
- 計測対象コード内で、一定タイミングごとに `profiler.step()` を呼びます
- 実行後、http://ui.perfetto.dev/ でトレースを開きます

**注意点:**

- PyTorch profiler は、プログラム内で torch を直接使っていなくても CPU/GPU の双方で利用できます
- `wait/warmup/active` で設定した回数に達するまで `profiler.step()` を呼ぶ必要があります
- 一般には次の設定が有効です:
    - `wait`: 見たくない初期ステップを越えるのに十分長くする
    - `warmup`: 0 でも動く可能性はあるが、念のため 3 などを設定
    - `active`: 通常は 1 で十分（メモリ使用量を抑えられる）。必要なら増やして比較
    - `repeat`: 通常は 1。1 回計測シーケンスを実行して終了
    - 公式資料: [PyTorch profiler schedule documentation](https://docs.pytorch.org/docs/stable/profiler.html#torch.profiler.schedule)
- CPU コードでは pyspy / pytorch profiler の両方で階層的フレームグラフが見られます
    - `step()` の `wait` により不要な初期化部分を除外でき、`active` により安定した時間を取得できます
    - また pytorch profiler は（おそらく）統計サンプリング分布ではなく実際の呼び出し系列を示します
- GPU コードでは直接の階層ビューは得られません
    - ただし各カーネル launch 時刻と実行時間は高精度で確認できます
    - launch オーバーヘッドが隠れていない場合、カーネル間の白い隙間として明確に見えます
    - Python 側階層ビューと GPU カーネルビューを厳密に揃えたい場合は、各 step 前に `sync()` を呼ぶ方法があります
        - その分レイテンシは増えます（例: 2 倍程度遅くなることがある）
        - 代わりに Python 側と GPU 側の対応を信頼できます

例えば次のようにします。
```bash
# 物理ステップ後に profiler を進める
if self.profiler is not None:
    qd.sync()  # profiling 前に Quadrants の GPU 処理完了を保証
    self.profiler.step()
```

## Quadrants カーネル内部の計測

Torch profiler が記録するのは CUDA カーネル時間であり、Quadrants カーネルそのものではありません。
これは CPU-only profiler（pyspy + sync など）よりは 1 段深い情報ですが、
さらに GPU カーネル内部のコードブロックを（実際には GPU スレッド/ブロック単位で）計測したい場合は `clock_counter` を使えます。

まず計測対象を enum で定義します。

```bash
from enum import IntEnum

class Time(IntEnum):
    LineSearch = 1
    Step2 = 2
    UpdateConstraint = 3
    HessianIncremental = 4
    UpdateGradient = 5
    StepLast = 6
```

次に `qd.i64` テンソル（例: `timers`）を渡し、カーネル内で次のように計測します。

```bash
@qd.kernel
def k1(... previous args, times: qd.types.NDArray[qd.i64, 1]:
	start = qd.clock_counter()
	linesearch()
	end = qd.clock_counter()
  if i_b == 0:
      times[Time.LineSearch, it] = end - start
  start = end

  step2()
	end = qd.clock_counter()
  if i_b == 0:
      times[Time.Step2, it] = end - start
  start = end

  update_constraint()
	end = qd.clock_counter()
  if i_b == 0:
      times[Time.UpdateConstraint, it] = end - start
  start = end
```

結果処理の例は `examples/speed_benchmark/timers.py` を参照してください。
