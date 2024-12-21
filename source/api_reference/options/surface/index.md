# 表面

一个``Surface``对象封装了用于渲染实体或其子组件（链接、几何体等）的所有视觉信息。
表面包含不同类型的纹理：diffuse_texture、specular_texture、roughness_texture、metallic_texture、transmission_texture、normal_texture 和 emissive_texture。每一个都是一个 `gs.textures.Texture` 对象。

:::{note}
大多数高级表面类型仅支持使用 `RayTracer` 渲染后端的相机。如果使用 `Rasterizer`，则只会渲染颜色。
:::

```{toctree}
:maxdepth: 2

surface
plastic/index
metal/index
emission/index
glass/index
```
