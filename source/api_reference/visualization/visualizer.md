# `Visualizer`

The orchestrator behind `scene.visualizer`, created automatically with every scene. It owns the interactive viewer, the camera sensors, and the renderer backend, and it refreshes them when you call `scene.visualizer.update()`. You rarely construct or call it directly: add cameras with `scene.add_camera(...)`, open the viewer with `show_viewer=True`, and drive both by stepping the scene and calling `update()` each step. For usage, see {doc}`/user_guide/interaction/visualization`.

## API reference

```{eval-rst}
.. autoclass:: genesis.vis.Visualizer
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`viewer`: the interactive window
- {doc}`camera`: camera sensors for off-screen rendering
- {doc}`renderers/index`: renderer backends
