# 表面 (Surface)

`Surface` 对象封装了用于渲染实体或其子组件（如链接、几何体等）的所有视觉属性。

## 纹理类型

表面包含以下类型的纹理，每个纹理都是 `gs.textures.Texture` 对象：

- diffuse_texture（漫反射纹理）
- specular_texture（镜面反射纹理）
- roughness_texture（粗糙度纹理）
- metallic_texture（金属度纹理）
- transmission_texture（透射纹理）
- normal_texture（法线纹理）
- emissive_texture（发光纹理）

:::{note}
注意：大多数高级表面类型仅支持使用 `RayTracer` 渲染后端的相机。使用 `Rasterizer` 时，只会渲染基础颜色。
:::

```{toctree}
:maxdepth: 2

surface
plastic/index
metal/index
emission/index
glass/index
```
