# Rendering

Genesis World renders a scene through cameras that you add before `build()`. Each camera can produce RGB, depth, segmentation, and normal images, and can record video. The renderer behind a camera decides the trade-off between speed and image quality: the rasterizer is fast and runs everywhere, the ray tracers produce physically based images, and the batch renderer renders every environment at once for vision-based training.

- {doc}`Cameras <cameras>`: add a camera, render images, record video, and choose a renderer.

```{toctree}
:hidden:
:maxdepth: 1

cameras
surfaces_textures
nyx_renderer
```
