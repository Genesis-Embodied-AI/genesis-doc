# `Mesh`

## 概述
`Mesh` 是 Genesis 自己的三角网格对象，它是 `trimesh.Trimesh` 的包装器，提供了一些额外的功能和属性。

## 主要功能
- 支持凸化（convexification）和简化（decimation）处理
- 提供网格重网格化（remeshing）和四面体化（tetrahedralization）功能
- 支持从多种格式加载网格（如 OBJ、GLTF、USD 等）
- 提供粒子采样功能
- 支持表面和纹理设置


```{eval-rst}  
.. autoclass:: genesis.engine.mesh.Mesh
    :members:
    :show-inheritance:
    :undoc-members:
```