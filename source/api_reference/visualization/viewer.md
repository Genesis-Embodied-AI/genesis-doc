# Viewer

The interactive window that renders a scene in real time, with mouse and keyboard camera controls. It is optional: pass `show_viewer=True` to `gs.Scene(...)` to open it, and omit it (or pass `show_viewer=False`) to run headless. The viewer always uses the rasterizer backend, independent of the scene's `renderer`. For the walkthrough, mouse and keyboard controls, and the `gs` command-line tools, see {doc}`/user_guide/interaction/visualization`.

The viewer is configured by two options objects: `ViewerOptions` sets its initial camera pose, resolution, and refresh rate; `VisOptions` sets viewer-independent visualization such as lighting, world-frame display, and segmentation level.

## Options

```{eval-rst}
.. autoclass:: genesis.options.ViewerOptions
```

```{eval-rst}
.. autoclass:: genesis.options.VisOptions
```

## Viewer

```{eval-rst}
.. autoclass:: genesis.vis.viewer.Viewer
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`visualizer`: the orchestrator that owns the viewer, cameras, and renderer
- {doc}`lights`: lighting the scene through `VisOptions`
- {doc}`/user_guide/interaction/visualization`: the interactive viewer and `gs` tools
