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

## See also

- {doc}`/user_guide/configuration/initialization`: what `gs.init()` and `gs.destroy()` do.
- {doc}`/user_guide/sensing/custom_sensors/index`: writing a custom sensor, another extension point.
