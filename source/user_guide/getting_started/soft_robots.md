# 🐛 软体机器人

## 体积肌肉模拟

Genesis 用 MPM 和 FEM 两种方式模拟软体机器人的肌肉。下面用简单的球形机器人演示正弦波驱动。

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

展示效果:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/muscle.mp4" type="video/mp4">
</video>

实现这个效果只需两个关键步骤:

* 创建软体机器人时用 `gs.materials.MPM.Muscle` 或 `gs.materials.FEM.Muscle` 作为材料
* 仿真时用 `robot_mpm.set_actuation` 或 `robot_fem.set_actuation` 设置肌肉驱动

默认情况下,肌肉覆盖整个机器人身体,方向垂直于地面 `[0, 0, 1]`。

下面用蠕虫爬行的例子演示如何设置多肌肉组和方向。(完整代码见 [tutorials/advanced_worm.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/examples/tutorials/advanced_worm.py))

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

效果:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/worm.mp4" type="video/mp4">
</video>

几个要点:

* 用 `gs.materials.MPM.Muscle` 时设置 `n_groups = 4` 表示最多可以有4个不同的肌肉
* 用 `robot.set_muscle` 设置肌肉,需要 `muscle_group` 和 `muscle_direction` 两个输入,长度跟 `n_units` 相同。MPM 中是粒子数量,FEM 中是元素数量
* `muscle_group` 是从 `0` 到 `n_groups - 1` 的整数数组,表示每个单元属于哪个肌肉组
* `muscle_direction` 是浮点数数组,指定肌肉方向向量。要注意数组需要自己归一化
* 蠕虫例子简单地把身体分为上前、上后、下前和下后四部分,用 `lu_thresh` 作上下阈值,用 `fh_thresh` 作前后阈值
* 有了4个肌肉组后,`set_actuation` 的输入就是形状为 `(4,)` 的数组

## 混合(刚体和软体)机器人

另一种软体机器人是用刚体内骨骼驱动软体外皮,也就是混合机器人。Genesis 支持混合机器人,下面用两节骨骼包软皮推球的例子演示。

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
        material_rigid=gs.materials.Rigid(
            gravity_compensation=1.,
        ),
        material_soft=gs.materials.MPM.Muscle( # 允许设置组
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

效果:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

要点:

* 用 `gs.materials.Hybrid` 指定混合机器人,由 `gs.materials.Rigid` 和 `gs.materials.MPM.Muscle` 组成。只支持 MPM,且必须用 Muscle 类因为内部用了它的 `muscle_group`
* 控制时用类似刚体机器人的接口,如 `control_dofs_velocity`、`control_dofs_force`、`control_dofs_position`。控制维度跟内部骨骼自由度相同(例子中是2)
* 皮肤由内部骨骼形状决定,`thickness` 参数控制包裹厚度
* 默认用骨骼形状生长皮肤,由 `morph` 指定(例子用 `urdf/simple/two_link_arm.urdf`)。`func_instantiate_soft_from_rigid` 定义如何根据刚体 `morph` 生长皮肤,有默认实现也可以自定义
* 当 `morph` 是 `Mesh` 时网格指定软体外形,内部骨骼根据皮肤生长,由 `func_instantiate_rigid_from_soft` 定义,默认实现是3D网格骨架化
* `func_instantiate_rigid_soft_association` 定义骨骼和皮肤如何关联,默认找最近粒子
