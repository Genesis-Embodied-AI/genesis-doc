# Extending Genesis World

If you build a package on top of Genesis World that needs to set up and tear down its own resources, GPU buffers, a renderer, a background service, you can tie that lifecycle to Genesis itself. Register a pair of callbacks and Genesis runs your setup on `gs.init()` and your teardown on `gs.destroy()`, so your extension comes up and goes down in lockstep with the engine.

## Registering a module

`gs.register_external_module(init_fun, destroy_fun)` takes two no-argument callables:

```python
import genesis as gs

def my_init():
    # allocate resources that depend on the active backend and device
    ...

def my_destroy():
    # release them
    ...

gs.register_external_module(my_init, my_destroy)

gs.init(backend=gs.gpu)  # my_init() runs here, after core initialization
# ... use Genesis and your extension ...
gs.destroy()             # my_destroy() runs here
```

- **`init_fun`** runs once, immediately after Genesis finishes initializing. If Genesis is *already* initialized when you register, `init_fun` runs right away instead.
- **`destroy_fun`** runs when `gs.destroy()` is called. Genesis also registers `destroy()` with `atexit`, so teardown happens on normal interpreter exit even if you do not call it yourself.

Register before `gs.init()` when you can, so setup happens as part of a single, ordered initialization.

## Unregistering

`gs.unregister_external_module(init_fun, destroy_fun)` removes the pair. The registry keys on the exact function objects you passed, so unregister with the same two callables you registered:

```python
gs.unregister_external_module(my_init, my_destroy)
```

:::{note}
Because the two callables identify the registration, pass named functions (or hold onto the references) rather than throwaway lambdas, otherwise you cannot unregister them later.
:::

## Writing a custom recorder

The built-in file writers and plotters cover most needs, but you can capture data any way you like by subclassing `genesis.recorders.Recorder` and passing your options to `scene.start_recording`. A recorder follows a five-method lifecycle driven by the scene, not called directly:

1. **`__init__`** configures the recorder from its options.
2. **`build()`** initializes resources (called during `scene.build()`).
3. **`process(data, cur_time)`** handles each sampled value during recording.
4. **`cleanup()`** finalizes and releases resources (called when recording stops).
5. **`reset(envs_idx=None)`** resets state for a new episode.

```python
import genesis as gs
from genesis.recorders import Recorder

class MyRecorder(Recorder):
    def __init__(self, manager, options, data_func):
        super().__init__(manager, options, data_func)
        self.data_buffer = []

    def build(self):
        super().build()
        self.data_buffer = []

    def process(self, data, cur_time):
        self.data_buffer.append({"time": cur_time, "data": data})

    def cleanup(self):
        print(f"Recorded {len(self.data_buffer)} samples")
        self.data_buffer = []

    def reset(self, envs_idx=None):
        self.data_buffer = []
```

For the recording workflow and the built-in recorders, see {doc}`/user_guide/sensing/recorders`.

## See also

- {doc}`/user_guide/configuration/initialization`: what `gs.init()` and `gs.destroy()` do.
- {doc}`/user_guide/sensing/custom_sensors/index`: writing a custom sensor, another extension point.
- {doc}`/api_reference/recording/recorder`: the `Recorder` base-class reference.
