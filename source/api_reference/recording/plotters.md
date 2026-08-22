# Plotters

A plotter visualizes sampled data live as the scene steps, and can save the animation. Pass one as the `rec_options` argument of `scene.start_recording`. See {doc}`index` for the recording workflow and the shared options (`hz`, `buffer_size`) that every plotter inherits.

A data function that returns a `dict` becomes one labeled subplot per key.

## `gs.recorders.PyQtLinePlot`

Draws a live line plot with PyQtGraph. The fastest option for high-rate time-series data, at the cost of a PyQt dependency.

```{eval-rst}
.. autoclass:: genesis.options.recorders.PyQtLinePlot

.. autoclass:: genesis.recorders.plotters.PyQtLinePlotter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.MPLLinePlot`

Draws a live line plot with Matplotlib. Use it for time-series data when you want a Matplotlib figure.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLLinePlot

.. autoclass:: genesis.recorders.plotters.MPLLinePlotter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.MPLImagePlot`

Displays a 2D array as a live image or heatmap, for example a camera frame or a sensor grid.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLImagePlot

.. autoclass:: genesis.recorders.plotters.MPLImagePlotter
    :members:
    :undoc-members:
    :show-inheritance:
```

## `gs.recorders.MPLVectorFieldPlot`

Draws a live vector field (quiver plot) from an array of 2D or 3D vectors.

```{eval-rst}
.. autoclass:: genesis.options.recorders.MPLVectorFieldPlot

.. autoclass:: genesis.recorders.plotters.MPLVectorFieldPlotter
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`index`: the recording workflow and shared recorder options.
- {doc}`file_writers`: writing data to a file instead of plotting.
