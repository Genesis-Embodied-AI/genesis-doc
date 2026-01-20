# Measure performance in Genesis and gstaichi

## Measuring gstaichi kernel execution time, and checking launch latency

Add pytorch profiler to the code, e.g.:

```bash
parser.add_argument(
    "--profile", action="store_true", default=False,
    help="Enable PyTorch profiling"
)
[...]

profiler = None
if args.profile:
    warmup={args.profile_warmup}, "
                    f"active={args.profile_active}, repeat={args.profile_repeat}")

    profiler_dir = os.path.join(en.log_dir, "profiler")
    os.makedirs(profiler_dir, exist_ok=True)

    schedule=torch.profiler.schedule(
        wait=80,
        warmup=3,
        active=1,
        repeat=1
    )
    print('schedule', schedule)
    profiler = torch.profiler.profile(
        activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
        schedule=schedule,
        record_shapes=False,
        profile_memory=False,
        with_stack=True,
        with_flops=False,
    )
    profiler.__enter__()  # Start the profiler context
```

- within the code you wish to profile, call `profiler.step()` at regular times
- after running the code, dump the trace as a chrome trace:

```bash
if profiler is not None:
    profiler.__exit__(None, None, None)  # Exit the profiler context
    profiler.export_chrome_trace("trace.json")
```
- open the trace in http://ui.perfetto.dev/

**Notes:**

- pytorch profiler can be used both for CPU and for GPU, even if torch is not used even a tiny bit in the program
- you’ll need to call profiler.step() at least enough times to match what you have put in wait/warmup/active
- generally you want:
    - `wait` to be long enough to get past any initial steps you don’t want to look at
    - `warmup` not sure if needs to be non-0, but I put 3, just in case
    - `active` ⇒ 1 is generally enough, and will reduce memory used. You can experiment with larger values if you wish, of course
    - `repeat` should be 1 in general: run the sequence of steps once, then stop profiling
    - see official documentation [PyTorch profiler schedule documentation](https://docs.pytorch.org/docs/stable/profiler.html#torch.profiler.schedule)
- for cpu code, both pyspy and pytorch profiler will give a hierarchical flame graph style view
    - however, the step() ‘wait’ functionality means you’ll skip all the initialization stuff at the start, that you’re not interested in, and the ‘active’ functionality means you’ll get consistent times
    - also, pytorch profiler shows the actual sequence of calls, rather than the statistically sampled distribution (I think)
- for gpu code, you don’t directly get any sort of hierarchy
    - you do however have very precise duration of each kernel launch time and duration
    - and you can clearly see any non-hidden kernel launch overhead, which is visible as white gaps between each kernel
    - if you do want a correspondance/alignment with the python-side code hierarchy, you can modify the code to call `sync()`, just before each step
        - this will add some latency (e.g. 2x slower, for example)
        - but means you can trust the alignment between the python hierarchical view and the gpu kernel view

For example, something like:
```bash
# Step the profiler after the physics step
if self.profiler is not None:
    ti.sync()  # Ensure all Taichi GPU operations complete before profiling
    self.profiler.step()
```

## Within gstaichi kernels

Create an enum with the things you will want to measure, e.g.:

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

Pass in a tensor of ti.64, e.g. timers. Then, inside the kernel, do things like:

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