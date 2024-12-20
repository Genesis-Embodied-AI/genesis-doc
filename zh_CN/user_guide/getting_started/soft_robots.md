# 🐛 软体机器人

## 体积肌肉模拟

Genesis 支持使用 MPM 和 FEM 进行软体机器人的体积肌肉模拟。在以下示例中，我们展示了一个非常简单的软体机器人，其球体身体由正弦波控制信号驱动。

```python
import numpy as np
import genesis as gs


########################## 初始化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

########################## 创建场景 ##########################
dt = 5e-4
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        substeps=10,
        gravity=(0, 0, 0),
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 0, 0.8),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    mpm_options=gs.options.MPMOptions(
        dt=dt,
        lower_bound=(-1.0, -1.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
    ),
    fem_options=gs.options.FEMOptions(
        dt=dt,
        damping=45.,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=False,
    ),
)

########################## 实体 ##########################
scene.add_entity(morph=gs.morphs.Plane())

E, nu = 3.e4, 0.45
rho = 1000.

robot_mpm = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, 0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.MPM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='neohooken',
    ),
)

robot_fem = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.5, -0.2, 0.3),
        radius=0.1,
    ),
    material=gs.materials.FEM.Muscle(
        E=E,
        nu=nu,
        rho=rho,
        model='stable_neohooken',
    ),
)

########################## 构建 ##########################
scene.build()

########################## 运行 ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0.2 * (0.5 + np.sin(0.01 * np.pi * i))])

    robot_mpm.set_actuation(actu)
    robot_fem.set_actuation(actu)
    scene.step()
```

这是你将看到的效果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/muscle.mp4" type="video/mp4">
</video>

大部分代码与实例化常规可变形实体相当标准。只有两个小差异实现了这个效果：

* 在实例化软体机器人 `robot_mpm` 和 `robot_fem` 时，我们分别使用了材料 `gs.materials.MPM.Muscle` 和 `gs.materials.FEM.Muscle`。
* 在进行仿真步进时，我们使用 `robot_mpm.set_actuation` 或 `robot_fem.set_actuation` 来设置肌肉的驱动。

默认情况下，只有一个肌肉覆盖整个机器人身体，肌肉方向垂直于地面 `[0, 0, 1]`。

在下一个示例中，我们展示了如何通过设置肌肉组和方向来模拟蠕虫向前爬行，如下所示。（完整脚本可以在 [tutorials/advanced_worm.py](https://github.com/zhouxian/Genesis-dev/tree/main/examples/tutorials/advanced_worm.py) 中找到。）

```python
########################## 实体 ##########################
worm = scene.add_entity(
    morph=gs.morphs.Mesh(
        file='meshes/worm/worm.obj',
        pos=(0.3, 0.3, 0.001),
        scale=0.1,
        euler=(90, 0, 0),
    ),
    material=gs.materials.MPM.Muscle(
        E=5e5,
        nu=0.45,
        rho=10000.,
        model='neohooken',
        n_groups=4,
    ),
)

########################## 设置肌肉 ##########################
def set_muscle_by_pos(robot):
    if isinstance(robot.material, gs.materials.MPM.Muscle):
        pos = robot.get_state().pos
        n_units = robot.n_particles
    elif isinstance(robot.material, gs.materials.FEM.Muscle):
        pos = robot.get_state().pos[robot.get_el2v()].mean(1)
        n_units = robot.n_elements
    else:
        raise NotImplementedError

    pos = pos.cpu().numpy()
    pos_max, pos_min = pos.max(0), pos.min(0)
    pos_range = pos_max - pos_min

    lu_thresh, fh_thresh = 0.3, 0.6
    muscle_group = np.zeros((n_units,), dtype=int)
    mask_upper = pos[:, 2] > (pos_min[2] + pos_range[2] * lu_thresh)
    mask_fore = pos[:, 1] < (pos_min[1] + pos_range[1] * fh_thresh)
    muscle_group[ mask_upper &  mask_fore] = 0 # 上前身体
    muscle_group[ mask_upper & ~mask_fore] = 1 # 上后身体
    muscle_group[~mask_upper &  mask_fore] = 2 # 下前身体
    muscle_group[~mask_upper & ~mask_fore] = 3 # 下后身体

    muscle_direction = np.array([[0, 1, 0]] * n_units, dtype=float)

    robot.set_muscle(
        muscle_group=muscle_group,
        muscle_direction=muscle_direction,
    )

set_muscle_by_pos(worm)

########################## 运行 ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0, 0, 0, 1. * (0.5 + np.sin(0.005 * np.pi * i))])

    worm.set_actuation(actu)
    scene.step()
```

这是你将看到的效果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/worm.mp4" type="video/mp4">
</video>

代码片段中值得注意的几点：

* 在指定材料 `gs.materials.MPM.Muscle` 时，我们设置了一个额外的参数 `n_groups = 4`，这意味着这个机器人最多可以有 4 个不同的肌肉。
* 我们可以通过调用 `robot.set_muscle` 来设置肌肉，该函数接受 `muscle_group` 和 `muscle_direction` 作为输入。两者的长度都与 `n_units` 相同，在 MPM 中 `n_units` 是粒子的数量，而在 FEM 中 `n_units` 是元素的数量。`muscle_group` 是一个从 `0` 到 `n_groups - 1` 的整数数组，表示机器人身体的一个单元属于哪个肌肉组。`muscle_direction` 是一个浮点数数组，指定肌肉方向的向量。请注意，我们不进行归一化，因此您可能需要确保输入的 `muscle_direction` 已经归一化。
* 我们设置这个蠕虫示例的肌肉的方法是简单地将身体分为四部分：上前、上后、下前和下后身体，使用 `lu_thresh` 作为上下阈值，使用 `fh_thresh` 作为前后阈值。
* 现在给定四个肌肉组，在通过 `set_actuation` 设置控制时，驱动输入是一个形状为 `(4,)` 的数组。

## 混合（刚体和软体）机器人

另一种软体机器人是使用刚体内骨骼驱动软体外皮，或更准确地说，混合机器人。由于已经实现了刚体和软体动力学，Genesis 也支持混合机器人。以下示例是一个具有两节骨骼的混合机器人，包裹着软皮肤，推动一个刚性球。

```python
import numpy as np
import genesis as gs


########################## 初始化 ##########################
gs.init(seed=0, precision='32', logging_level='debug')

######################## 创建场景 ##########################
dt = 3e-3
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        substeps=10,
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 1.3, 0.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        dt=dt,
        gravity=(0, 0, -9.8),
        enable_collision=True,
        enable_self_collision=False,
    ),
    mpm_options=gs.options.MPMOptions(
        dt=dt,
        lower_bound=( 0.0,  0.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
        gravity=(0, 0, 0), # 模拟重力补偿
        enable_CPIC=True,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
        visualize_mpm_boundary=False,
    ),
)

########################## 实体 ##########################
scene.add_entity(morph=gs.morphs.Plane())

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="urdf/simple/two_link_arm.urdf",
        pos=(0.5, 0.5, 0.3),
        euler=(0.0, 0.0, 0.0),
        scale=0.2,
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        mat_rigid=gs.materials.Rigid(
            gravity_compensation=1.,
        ),
        mat_soft=gs.materials.MPM.Muscle( # 允许设置组
            E=1e4,
            nu=0.45,
            rho=1000.,
            model='neohooken',
        ),
        thickness=0.05,
        damping=1000.,
        func_instantiate_rigid_from_soft=None,
        func_instantiate_soft_from_rigid=None,
        func_instantiate_rigid_soft_association=None,
    ),
)

ball = scene.add_entity(
    morph=gs.morphs.Sphere(
        pos=(0.8, 0.6, 0.1),
        radius=0.1,
    ),
    material=gs.materials.Rigid(rho=1000, friction=0.5),
)

########################## 构建 ##########################
scene.build()

########################## 运行 ##########################
scene.reset()
for i in range(1000):
    dofs_ctrl = np.array([
        1. * np.sin(2 * np.pi * i * 0.001),
    ] * robot.n_dofs)

    robot.control_dofs_velocity(dofs_ctrl)

    scene.step()
```

这是你将看到的效果：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

* 你可以使用材料 `gs.materials.Hybrid` 指定混合机器人，该材料由 `gs.materials.Rigid` 和 `gs.materials.MPM.Muscle` 组成。请注意，这里只支持 MPM，并且它必须是 Muscle 类，因为混合材料内部重用了 `Muscle` 实现的 `muscle_group`。
* 在控制机器人时，由于驱动来自内部刚体骨骼，因此有一个类似于刚体机器人的接口，例如 `control_dofs_velocity`、`control_dofs_force`、`control_dofs_position`。此外，控制维度与内部骨骼的自由度相同（在上述示例中为 2）。
* 皮肤由内部骨骼的形状决定，其中 `thickness` 决定了包裹骨骼时的皮肤厚度。
* 默认情况下，我们根据骨骼的形状生长皮肤，这由 `morph` 指定（在此示例中为 `urdf/simple/two_link_arm.urdf`）。`gs.materials.Hybrid` 的参数 `func_instantiate_soft_from_rigid` 具体定义了如何根据刚体 `morph` 生长皮肤。有一个默认实现 `default_func_instantiate_soft_from_rigid` 在 [genesis/engine/entities/hybrid_entity.py](https://github.com/zhouxian/Genesis-dev/blob/main/genesis/engine/entities/hybrid_entity.py) 中。你也可以实现自己的函数。
* 当 `morph` 是 `Mesh` 而不是 `URDF` 时，网格指定软体外部，内部骨骼根据皮肤形状生长。这由 `func_instantiate_rigid_from_soft` 定义。还有一个默认实现 `default_func_instantiate_rigid_from_soft`，它基本上实现了 3D 网格的骨架化。
* `gs.materials.Hybrid` 的参数 `func_instantiate_rigid_soft_association` 决定了每个骨骼部分如何与皮肤关联。默认实现是找到软皮肤中最接近刚体骨骼部分的粒子。
