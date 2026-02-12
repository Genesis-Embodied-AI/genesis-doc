# 🗂 配置系统

## 概述

Genesis 模拟框架围绕一个模块化和可扩展的配置系统构建。该系统允许用户通过结构化配置对象灵活地组合和控制模拟的不同方面——从低级物理求解器到高级渲染选项。

为了帮助你理解这些组件如何协同工作，我们从 Genesis 场景通常如何初始化的高级模板开始。此模板展示了如何编排模拟设置、求解器选项和实体级配置。

```python
# 初始化 Genesis
gs.init(...)

# 初始化场景
scene = gs.Scene(
    # 模拟与耦合
    sim_options=SimOptions(...),
    coupler_options=CouplerOptions(...),

    # 求解器
    tool_options=ToolOptions(...),
    rigid_options=RigidOptions(...),
    mpm_options=MPMOptions(...),
    sph_options=SPHOptions(...),
    fem_options=FEMOptions(...),
    sf_options=SFOptions(...),
    pbd_options=PBDOptions(...),

    # 可视化与渲染
    vis_options=VisOptions(...),
    viewer_options=ViewerOptions(...),
    renderer=Rasterizer(...),
)

# 添加实体
scene.add_entity(
    morph=gs.morphs...,
    material=gs.materials...,
    surface=gs.surfaces....,
)
```

如上所示，Genesis 中的场景由以下组合定义：

- [模拟与耦合](#模拟--耦合)：定义全局模拟参数和不同求解器如何交互。
- [求解器](#求解器)：为不同模拟方法（例如刚体、流体、布料）配置物理行为。
- [可视化与渲染](#可视化--渲染)：自定义运行时可视化和最终渲染选项。
- 对于添加到场景的每个实体：
    - [Morph](#morph)：定义实体的几何或结构。
    - [Material](#material)：指定与相应物理求解器相关的材质属性。
    - [Surface](#surface)：控制视觉外观和表面渲染。

## 模拟与耦合

此配置定义了模拟的全局结构以及不同物理求解器如何耦合。这些选项控制模拟循环的"骨架"，例如时间步进、稳定性和求解器互操作性。

- `SimOptions`：设置全局模拟参数——时间步长、重力、阻尼和数值积分器。
- `CouplerOptions`：配置多物理场交互——例如，刚性工具如何与软可变形体交互，或流体如何流过多孔材料。

定义于 [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py)。

## 求解器

求解器是特定物理模型的核心。每个求解器封装了特定材料或系统的模拟算法——刚体、流体、可变形体等。用户可以根据场景启用或禁用求解器。
- `RigidOptions`：具有接触、碰撞和约束的刚体动力学。
- `MPMOptions`：用于弹性、塑性、颗粒、流体材料的物质点法求解器。
- `SPHOptions`：用于流体和颗粒流的平滑粒子流体动力学求解器。
- `FEMOptions`：用于弹性材料的有限元法求解器。
- `SFOptions`：用于基于欧拉的气体模拟的稳定流体求解器。
- `PBDOptions`：用于布料、体积可变形对象、液体和粒子的基于位置的动力学求解器。
- `ToolOptions`：临时设置。将被弃用。

定义于 [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py)。

## 可视化与渲染

此配置控制实时可视化（在调试和开发期间有用）和最终渲染输出（用于演示、分析或媒体）。它控制用户如何与模拟进行视觉交互和感知。
- `ViewerOptions`：配置交互式查看器的属性。
- `VisOptions`：配置独立于查看器或相机的可视化相关属性。
- `Renderer`（Rasterizer 或 Raytracer）：定义渲染后端，包括光照、着色和后处理效果。支持光栅化或光线追踪。

定义于 [genesis/options/vis.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/vis.py) 和 [genesis/options/renderers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/renderers.py)。

## Morph

Morphs 定义实体的形状和拓扑结构。这包括基本几何体（例如球体、盒子）、结构化资源（例如关节臂）。Morphs 形成材质和物理操作的几何基础。
- `Primitive`：所有形状基本体的 Morph。
    - `Box`：由盒子形状定义的 Morph。
    - `Cylinder`：由圆柱形状定义的 Morph。
    - `Sphere`：由球体形状定义的 Morph。
    - `Plane`：由平面形状定义的 Morph。
- `FileMorph`：
    - `Mesh`：从网格文件加载的 Morph。
        - `MeshSet`：网格的集合。
    - `MJCF`：从 MJCF 文件加载的 Morph。此 Morph 仅支持刚体实体。
    - `URDF`：从 URDF 文件加载的 Morph。此 Morph 仅支持刚体实体。
    - `Drone`：从 URDF 文件加载用于创建无人机实体的 Morph。
- `Terrain`：用于创建刚性地形的 Morph。
- `NoWhere`：为发射器保留。仅供内部使用。

定义于 [genesis/options/morphs.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/morphs.py)。

## Material

材质定义物体如何响应物理力。这包括刚度、摩擦、弹性、阻尼和求解器特定的材质参数。材质还决定实体如何与其他对象和求解器交互。
- `Rigid`：刚体和关节体。
- `MPM`：物质点法。
    - `Elastic`
    - `ElastoPlastic`
    - `Liquid`
    - `Muscle`
    - `Sand`
    - `Snow`
- `FEM`：有限元法。
    - `Elastic`
    - `Muscle`
- `PBD`：基于位置的动力学。
    - `Cloth`
    - `Elastic`
    - `Liquid`
    - `Particle`
- `SF`：稳定流体。
    - `Smoke`
- `Hybrid`：刚体骨骼驱动软皮肤。
- `Tool`：临时且将被弃用。

这些可以在 [genesis/engine/materials](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/materials) 中找到。

## Surface

表面定义实体的视觉外观。它们包括颜色、纹理、反射率、透明度等渲染属性。表面是实体内部结构和渲染器之间的接口。

- `Default`：基本上是 `Plastic`。
- `Plastic`：塑料表面是最基本的表面类型。
    - `Rough`：具有适当参数的粗糙表面的快捷方式。
    - `Smooth`：具有适当参数的平滑表面的快捷方式。
    - `Reflective`：默认灰色的碰撞几何体快捷方式。
    - `Collision`：具有适当参数的粗糙塑料表面的快捷方式。
- `Metal`
    - `Iron`：`metal_type = 'iron'` 的金属表面快捷方式。
    - `Aluminium`：`metal_type = 'aluminium'` 的金属表面快捷方式。
    - `Copper`：`metal_type = 'copper'` 的金属表面快捷方式。
    - `Gold`：`metal_type = 'gold'` 的金属表面快捷方式。
- `Glass`
    - `Water`：水表面的快捷方式（使用具有适当值的 Glass 表面）。
- `Emission`：发光表面。此表面发射光。

定义于 [genesis/options/surfaces.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/surfaces.py)。
