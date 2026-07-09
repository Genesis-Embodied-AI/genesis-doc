# Plotters

A plotter visualizes sampled data live as the scene steps, and can save the animation. Pass one as the `rec_options` argument of `scene.start_recording`. See {doc}`index` for the recording workflow and the shared options (`hz`, `buffer_size`) that every plotter inherits.

A data function that returns a `dict` becomes one labeled subplot per key.

## `gs.recorders.PyQtLinePlot`

Live line plot backed by PyQtGraph. The fastest option for high-rate time-series data, at the cost of a PyQt dependency.

```{eval-rst}
.. autoclass:: genesis.options.recorders.PyQtLinePlot
```

## `gs.recorders.MPLLinePlot`

Live line plot backed by Matplotlib. Use it for time-series data when a Matplotlib figure is preferred.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLLinePlot
```

## `gs.recorders.MPLImagePlot`

Displays a 2D array as a live image or heatmap, for example a camera frame or a sensor grid.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLImagePlot
```

## `gs.recorders.MPLVectorFieldPlot`

Draws a live vector field (quiver plot) from an array of 2D or 3D vectors.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLVectorFieldPlot
```

## See also

- {doc}`index`: the recording workflow and shared recorder options.
- {doc}`file_writers`: writing data to a file instead of plotting.
