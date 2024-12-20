# 🌊 超越刚体

Genesis 统一了多种物理求解器，支持超越刚体动力学的模拟。`求解器` 本质上是一组物理模拟算法，用于处理特定材料。在本教程中，我们将介绍三种流行的求解器，并使用它们来模拟具有不同物理特性的实体：

- [光滑粒子流体动力学 (SPH) 求解器](#sph)
- [材料点法 (MPM) 求解器](#mpm)
- [基于位置的动力学 (PBD) 求解器](#pbd)

## 使用 SPH 求解器进行液体模拟 <a id="sph"></a>

首先，让我们看看如何模拟一个水立方。创建一个空场景并添加一个平面：

```python
import genesis as gs

########################## 初始化 ##########################
gs.init()

########################## 创建场景 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    sph_options=gs.options.SPHOptions(
        lower_bound   = (-0.5, -0.5, 0.0),
        upper_bound   = (0.5, 0.5, 1),
        particle_size = 0.01,
    ),
    vis_options=gs.options.VisOptions(
        visualize_sph_boundary = True,
    ),
    show_viewer = True,
)

########################## 实体 ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)
```

这里有几点需要注意：

- 在配置 `sim_options` 时，我们使用了相对较小的 `dt` 和 `substeps=10`。这意味着在模拟器内部，每个 `step` 将模拟 10 个 `substep`，每个 `substep_dt = 4e-3 / 10`。在之前处理刚体时，我们没有设置这个参数，使用的是默认设置 (`substeps=1`)，即每步只运行 1 个子步。
- 如前所述，我们使用 `options` 来配置每个不同的求解器。由于我们使用的是 `SPHSolver`，因此需要通过 `sph_options` 配置其属性。在此示例中，我们设置了求解器的边界，并将粒子大小指定为 0.01 米。SPHSolver 是一种拉格朗日求解器，使用粒子来表示对象。
- 在 `vis_options` 中，我们指定希望在渲染视图中看到 SPH 求解器的边界。

接下来，让我们添加一个水块实体并开始模拟！
当我们添加块时，将其从刚性块变为水块的唯一不同之处在于设置 `material`。实际上，之前处理刚体时，这个参数默认设置为 `gs.materials.Rigid()`。由于我们现在使用 SPH 求解器进行液体模拟，因此选择 `SPH` 类别下的 `Liquid` 材料：

```python
liquid = scene.add_entity(
    material=gs.materials.SPH.Liquid(
        sampler='pbs',
    ),
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.65),
        size = (0.4, 0.4, 0.4),
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 0.8, 1.0),
        vis_mode = 'particle',
    ),
)

########################## 构建 ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()
```

在创建 `Liquid` 材料时，我们设置了 `sampler='pbs'`。这配置了我们希望如何根据 `Box` 形态采样粒子。`pbs` 代表“基于物理的采样”，它运行一些额外的模拟步骤，以确保粒子以物理自然的方式排列。您还可以使用 `'regular'` 采样器，简单地使用网格格子模式采样粒子。如果您使用其他求解器（如 MPM），还可以使用 `'random'` 采样器。

您可能还注意到我们传递了一个额外的属性 -- `surface`。此属性用于定义实体的所有视觉属性。在这里，我们将水的颜色设置为蓝色，并通过设置 `vis_mod='particle'` 选择将其可视化为粒子。

成功运行后，您将看到水滴落并在平面上扩散，但受限于求解器边界：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/sph_liquid.mp4" type="video/mp4">
</video>

您可以通过以下方式获取实时粒子位置：

```
particles = liquid.get_particles()
```

**更改液体属性：** 您还可以调整液体的物理属性。例如，您可以增加其粘度 (`mu`) 和表面张力 (`gamma`)：

```python
material=gs.materials.SPH.Liquid(mu=0.02, gamma=0.02),
```

并观察行为的不同。享受吧！

完整脚本：

```python
import genesis as gs

########################## 初始化 ##########################
gs.init()

########################## 创建场景 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    sph_options=gs.options.SPHOptions(
        lower_bound   = (-0.5, -0.5, 0.0),
        upper_bound   = (0.5, 0.5, 1),
        particle_size = 0.01,
    ),
    vis_options=gs.options.VisOptions(
        visualize_sph_boundary = True,
    ),
    show_viewer = True,
)

########################## 实体 ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)

liquid = scene.add_entity(
    # 粘性液体
    # material=gs.materials.SPH.Liquid(mu=0.02, gamma=0.02),
    material=gs.materials.SPH.Liquid(),
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.65),
        size = (0.4, 0.4, 0.4),
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 0.8, 1.0),
        vis_mode = 'particle',
    ),
)

########################## 构建 ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()

# 获取粒子位置
particles = liquid.get_particles()
```

## 使用 MPM 求解器进行可变形物体模拟 <a id="mpm"></a>

MPM 求解器是一种非常强大的物理求解器，支持更广泛的材料。MPM 代表材料点法，使用混合拉格朗日-欧拉表示，即同时使用粒子和网格来表示对象。

在此示例中，让我们创建三个对象：

- 一个弹性立方体，可视化为 `'particles'`
- 一个液体立方体，可视化为 `'particles'`
- 一个弹塑性球体，可视化为原始球体网格，但根据内部粒子状态变形 (`vis_mode='visual'`)。这种将内部粒子状态映射到变形视觉网格的过程在计算机图形学中称为 *蒙皮*。

完整代码脚本：

```python
import genesis as gs

########################## 初始化 ##########################
gs.init()

########################## 创建场景 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound   = (-0.5, -1.0, 0.0),
        upper_bound   = (0.5, 1.0, 1),
    ),
    vis_options=gs.options.VisOptions(
        visualize_mpm_boundary = True,
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_fov=30,
    ),
    show_viewer = True,
)

########################## 实体 ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)

obj_elastic = scene.add_entity(
    material=gs.materials.MPM.Elastic(),
    morph=gs.morphs.Box(
        pos  = (0.0, -0.5, 0.25),
        size = (0.2, 0.2, 0.2),
    ),
    surface=gs.surfaces.Default(
        color    = (1.0, 0.4, 0.4),
        vis_mode = 'visual',
    ),
)

obj_sand = scene.add_entity(
    material=gs.materials.MPM.Liquid(),
    morph=gs.morphs.Box(
        pos  = (0.0, 0.0, 0.25),
        size = (0.3, 0.3, 0.3),
    ),
    surface=gs.surfaces.Default(
        color    = (0.3, 0.3, 1.0),
        vis_mode = 'particle',
    ),
)

obj_plastic = scene.add_entity(
    material=gs.materials.MPM.ElastoPlastic(),
    morph=gs.morphs.Sphere(
        pos  = (0.0, 0.5, 0.35),
        radius = 0.1,
    ),
    surface=gs.surfaces.Default(
        color    = (0.4, 1.0, 0.4),
        vis_mode = 'particle',
    ),
)


########################## 构建 ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()
```

请注意，要更改底层的物理材料，只需更改 `material` 属性。随意尝试其他材料类型（如 `MPM.Sand()` 和 `MPM.Snow()`），以及每种材料类型中的属性值。

预期渲染结果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/mpm.mp4" type="video/mp4">
</video>

## 使用 PBD 求解器进行布料模拟 <a id="pbd"></a>

PBD 代表基于位置的动力学。这也是一种拉格朗日求解器，使用粒子和边表示实体，并通过求解一组基于位置的约束来模拟其状态。它可用于模拟保持拓扑结构的 1D/2D/3D 实体。在此示例中，我们将看到如何使用 PBD 求解器模拟布料。

在此示例中，我们将添加两个方形布料实体：一个固定四个角，另一个仅固定一个角并落在第一块布料上。此外，我们将使用不同的 `vis_mode` 渲染它们。

创建场景并构建：

```python
import genesis as gs

########################## 初始化 ##########################
gs.init()

########################## 创建场景 ##########################

scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt       = 4e-3,
        substeps = 10,
    ),
    viewer_options=gs.options.ViewerOptions(
        camera_fov = 30,
        res        = (1280, 720),
        max_FPS    = 60,
    ),
    show_viewer = True,
)

########################## 实体 ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)

cloth_1 = scene.add_entity(
    material=gs.materials.PBD.Cloth(),
    morph=gs.morphs.Mesh(
        file='meshes/cloth.obj',
        scale=2.0,
        pos=(0, 0, 0.5), 
        euler=(0.0, 0, 0.0),
    ),
    surface=gs.surfaces.Default(
        color=(0.2, 0.4, 0.8, 1.0),
        vis_mode='visual',
    )
)

cloth_2 = scene.add_entity(
    material=gs.materials.PBD.Cloth(),
    morph=gs.morphs.Mesh(
        file='meshes/cloth.obj',
        scale=2.0,
        pos=(0, 0, 1.0), 
        euler=(0.0, 0, 0.0),
    ),
    surface=gs.surfaces.Default(
        color=(0.8, 0.4, 0.2, 1.0),
        vis_mode='particle',
    )
)

########################## 构建 ##########################
scene.build()
```

然后，让我们固定我们想要的角（粒子）。为此，我们提供了一个方便的工具，可以使用笛卡尔空间中的位置来定位粒子：

```python

cloth_1.fix_particle(cloth_1.find_closest_particle((-1, -1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((1, 1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((-1, 1, 1.0)))
cloth_1.fix_particle(cloth_1.find_closest_particle((1, -1, 1.0)))

cloth_2.fix_particle(cloth_2.find_closest_particle((-1, -1, 1.0)))

horizon = 1000
for i in range(horizon):
    scene.step()
```

预期渲染结果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/pbd_cloth.mp4" type="video/mp4">
</video>

:::{warning}
**2D 网格的蒙皮**

我们注意到在使用 2D 平面布料网格并设置 `vis_mode='visual'` 时存在一些问题，这是由于在计算重心权重时退化的伪逆矩阵计算导致的。如果您在上述示例中为布料添加非零欧拉角并使用 `vis_mode='visual'`，可能会注意到奇怪的可视化结果。我们将很快修复这个问题。
:::

***更多关于求解器耦合的教程即将推出！***
