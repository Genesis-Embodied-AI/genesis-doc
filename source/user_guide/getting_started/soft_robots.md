# 🐛 Soft Robots

## Volumetric muscle simulation

Genesis supports volumetric muscle simulation using MPM and FEM for soft robots. In the following example, we demonstrate an extremely simple soft robot with a sphere body, actuated by a sine-wave control signal.

```python
import numpy as np
import genesis as gs


########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

########################## create a scene ##########################
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt = 5e-4,
        substeps=10,
        gravity=(0, 0, 0),
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 0, 0.8),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(-1.0, -1.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
    ),
    fem_options=gs.options.FEMOptions(
        damping=45.0,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=False,
    ),
)

########################## entities ##########################
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

########################## build ##########################
scene.build()

########################## run ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0.2 * (0.5 + np.sin(0.01 * np.pi * i))])

    robot_mpm.set_actuation(actu)
    robot_fem.set_actuation(actu)
    scene.step()
```
This is what you will see:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/muscle.mp4" type="video/mp4">
</video>

Most of the code is pretty standard compared to instantiating regular deformable entities. There are only two small differences that do the trick:

* When instantiating soft robots `robot_mpm` and `robot_fem`, we use materials `gs.materials.MPM.Muscle` and `gs.materials.FEM.Muscle` respectively.
* When stepping the simulation, we use `robot_mpm.set_actuation` or `robot_fem.set_actuation` to set the actuation of the muscle.

By default, there is only one muscle that spans the entire robot body with the muscle direction perpendicular to the ground `[0, 0, 1]`.

In the next example, we show how to simulate a worm crawling forward by setting muscle groups and directions, as shown in the following. (The full script can be found in [tutorials/advanced_worm.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/examples/tutorials/advanced_worm.py).)

```python
########################## entities ##########################
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

########################## set muscle ##########################
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
    muscle_group[ mask_upper &  mask_fore] = 0 # upper fore body
    muscle_group[ mask_upper & ~mask_fore] = 1 # upper hind body
    muscle_group[~mask_upper &  mask_fore] = 2 # lower fore body
    muscle_group[~mask_upper & ~mask_fore] = 3 # lower hind body

    muscle_direction = np.array([[0, 1, 0]] * n_units, dtype=float)

    robot.set_muscle(
        muscle_group=muscle_group,
        muscle_direction=muscle_direction,
    )

set_muscle_by_pos(worm)

########################## run ##########################
scene.reset()
for i in range(1000):
    actu = np.array([0, 0, 0, 1. * (0.5 + np.sin(0.005 * np.pi * i))])

    worm.set_actuation(actu)
    scene.step()
```
This is what you will see:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/worm.mp4" type="video/mp4">
</video>

Several things that worth noticing in this code snippet:

* When specifying the material `gs.materials.MPM.Muscle`, we set an additional argument `n_groups = 4`, which means there can be at most 4 different muscles in this robot.
* We can set the muscle by calling `robot.set_muscle`, which takes `muscle_group` and `muscle_direction` as inputs. Both have the same length as `n_units`, where in MPM `n_units` is the number of particles while in FEM `n_units` is the number of elements. `muscle_group` is an array of integer ranging from `0` to `n_groups - 1`, indicating which muscle group an unit of the robot body belongs to. `muscle_direction` is an array of floating-point numbers that specify vectors for muscle direction. Note that we don't do normalization and thus you may want to make sure the input `muscle_direction` is already normalized.
* How we set the muscle of this worm example is simply breaking the body into four parts: upper fore, upper hind, lower fore, and lower hind body, using `lu_thresh` for thresholding between lower/upper and `fh_thresh` for thresholding between fore/hind.
* Now given four muscle groups, when setting the control via `set_actuation`, the actuation input is thus an array of shape `(4,)`.


## Hybrid (rigid-and-soft) robot

Another type of soft robot is using rigid-bodied inner skeleton to actuatuate soft-bodied outer skin, or more precisely speaking, hybrid robot. With both rigid-bodied and soft-bodied dynamics implemented already, Genesis also supports hybrid robot. The following example is a hybrid robot with a two-link skeleton wrapped by soft skin pushing a rigid ball.

```python
import numpy as np
import genesis as gs


########################## init ##########################
gs.init(seed=0, precision='32', logging_level='info')

######################## create a scene ##########################
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=3e-3,
        substeps=10,
    ),
    viewer_options= gs.options.ViewerOptions(
        camera_pos=(1.5, 1.3, 0.5),
        camera_lookat=(0.0, 0.0, 0.0),
        camera_fov=40,
    ),
    rigid_options=gs.options.RigidOptions(
        gravity=(0, 0, -9.8),
        enable_collision=True,
        enable_self_collision=False,
    ),
    mpm_options=gs.options.MPMOptions(
        lower_bound=( 0.0,  0.0, -0.2),
        upper_bound=( 1.0,  1.0,  1.0),
        gravity=(0, 0, 0), # mimic gravity compensation
        enable_CPIC=True,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
        visualize_mpm_boundary=False,
    ),
)

########################## entities ##########################
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
        material_soft=gs.materials.MPM.Muscle( # to allow setting group
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

########################## build ##########################
scene.build()

########################## run ##########################
scene.reset()
for i in range(1000):
    dofs_ctrl = np.array([
        1. * np.sin(2 * np.pi * i * 0.001),
    ] * robot.n_dofs)

    robot.control_dofs_velocity(dofs_ctrl)

    scene.step()
```
This is what you will see:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

* You can specify hybrid robot with the material `gs.materials.Hybrid`, which consists of `gs.materials.Rigid` and `gs.materials.MPM.Muscle`. Note that only MPM is supported here and it must be the Muscle class since the hybrid material reuses internally the `muscle_group` implemented for `Muscle`.
* When controlling the robot, given the actuation being from the inner rigid-bodied skeleton, there is a similar interface to rigid-bodied robot, e.g., `control_dofs_velocity`, `control_dofs_force`, `control_dofs_position`. Also, the control dimension is the same as the DoFs of the inner skeleton (in the above example, 2).
* The skin is determined by the shape of the inner skeleton, where `thickness` determines the skin thickness when wrapping the skeleton.
* By default, we grow skin based on the shape of the skeleton, which is specified by `morph` (in this example, the `urdf/simple/two_link_arm.urdf`). The argument `func_instantiate_soft_from_rigid` of `gs.materials.Hybrid` defines concretely how skin should grow based on the rigid-bodied `morph`. There is a default implementation `default_func_instantiate_soft_from_rigid` in [genesis/engine/entities/hybrid_entity.py](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/entities/hybrid_entity.py). You can also implement your own function.
* When `morph` is `Mesh` instead of `URDF`, the mesh specifies the soft outer body and the inner skeleton is grown based on the skin shape. This is defined by `func_instantiate_rigid_from_soft`. There is also a default implementation `default_func_instantiate_rigid_from_soft`, which basically implements skeletonization of 3D meshes.
* The argument `func_instantiate_rigid_soft_association` of `gs.materials.Hybrid` determines how each skeletal part is associated with skin. The default implementation is to find the closest particles of the soft skin to the rigid skeletal parts.
