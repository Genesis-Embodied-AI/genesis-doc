# 表面材质 (Surface)

`Surface` 对象封装了用于渲染实体或其子组件（links、geoms 等）的所有视觉信息。

表面材质包含不同类型的纹理：diffuse_texture、specular_texture、roughness_texture、metallic_texture、transmission_texture、normal_texture 和 emissive_texture。每一种都是 `gs.textures.Texture` 对象。

:::{note}
大多数高级表面材质类型仅在使用 `RayTracer` 渲染后端时受相机支持。如果使用 `Rasterizer`，则仅会渲染颜色。
:::


```{toctree}
:maxdepth: 2

surface
plastic/index
metal/index
emission/index
glass/index
```
