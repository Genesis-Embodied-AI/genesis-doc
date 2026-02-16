# 在 Genesis 中测量性能

## 测量内核执行时间，并检查启动延迟

将 pytorch profiler 添加到代码中，例如：

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
    # 注意这必须在上下文管理器之外
    profiler.export_chrome_trace("trace.json")
```
- 在要分析的代码中，定期调用 `profiler.step()`
- 运行后，在 http://ui.perfetto.dev/ 中打开 trace

**注意：**

- pytorch profiler 可以用于 CPU 和 GPU，即使程序中完全没有使用 torch
- 您需要调用足够多次的 profiler.step() 以匹配您在 wait/warmup/active 中设置的值
- 通常您想要：
    - `wait` 足够长以跳过您不想查看的任何初始步骤
    - `warmup` 不确定是否需要非零，但我设为 3，以防万一
    - `active` ⇒ 1 通常足够，会减少使用的内存。如果需要，您可以尝试更大的值
    - `repeat` 通常应为 1：运行步骤序列一次，然后停止分析
    - 参见官方文档 [PyTorch profiler schedule documentation](https://docs.pytorch.org/docs/stable/profiler.html#torch.profiler.schedule)
- 对于 cpu 代码，pyspy 和 pytorch profiler 都会给出层次化的火焰图样式视图
    - 但是，step() 的 'wait' 功能意味着您将跳过开始时您不感兴趣的所有初始化内容，而 'active' 功能意味着您将获得一致的时间
    - 此外，pytorch profiler 显示实际调用序列，而不是统计采样分布（我认为）
- 对于 gpu 代码，您不会直接获得任何层次结构
    - 但是，您可以非常精确地获得每个内核启动时间和持续时间
    - 您可以清楚地看到任何非隐藏的内核启动开销，它可见为每个内核之间的白色间隙
    - 如果您确实想要看到与 python 端层次视图对齐的 gpu 内核，这有助于理解 gpu 内核与什么相关，您可以修改代码以在每一步之前调用 `sync()`
        - 这会增加一些延迟（例如 2 倍慢）
        - 但意味着您可以信任 python 层次视图和 gpu 内核视图之间的对齐

例如：
```bash
# 在物理步骤后步进分析器
if self.profiler is not None:
    ti.sync()  # 确保所有 Taichi GPU 操作在分析前完成
    self.profiler.step()
```

## 在内核内部

Torch profiler 记录在 CUDA 内核中花费的时间，而不是 Taichi 内核。这已经比仅使用 CPU profiler（例如 pyspy）+ sync 更深入一层。但如果您想更深入，并在每个 GPU 线程（实际上是块）上分析单个 GPU 内核内的代码块，您可以使用 clock_counter。

首先，创建一个枚举，包含您想要测量的内容，例如：

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

传入一个 ti.64 的张量，例如 timers。然后，在内核内部，执行如下操作：

```bash
@ti.kernel
def k1(... previous args, times: ti.types.NDArray[ti.i64, 1]:
	start = ti.clock_counter()
	linesearch()
	end = ti.clock_counter()
  if i_b == 0:
      times[Time.LineSearch, it] = end - start
  start = end
  
  step2()
	end = ti.clock_counter()
  if i_b == 0:
      times[Time.Step2, it] = end - start
  start = end
    
  update_constraint()
	end = ti.clock_counter()
  if i_b == 0:
      times[Time.UpdateConstraint, it] = end - start
  start = end
```

有关处理结果的示例，请参见 [genesis/examples/speed_benchmark/timers.py](genesis/examples/speed_benchmark/timers.py)。
