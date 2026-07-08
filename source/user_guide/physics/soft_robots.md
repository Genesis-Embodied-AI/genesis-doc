# Soft robots

A soft robot is a deformable body with **muscle fibers** embedded in it. Instead of joint motors turning a rigid skeleton, you drive it by contracting those fibers: each actuation signal adds an active stress along the fiber direction, and the body deforms in response. This page shows how to build muscle-actuated soft robots and control them.

Genesis World simulates muscles with two deformable solvers, and you pick one through the entity's material:

- `gs.materials.MPM.Muscle`: the Material Point Method solver, actuated per **particle**.
- `gs.materials.FEM.Muscle`: the Finite Element Method solver, actuated per tetrahedral **element**.

Both share the same control interface, so you can swap solvers without rewriting your control loop. The {doc}`beyond_rigid_bodies` tutorial covers the underlying solvers in more depth.

:::{note}
MPM and FEM are compute-heavy. Run them on the GPU by passing `backend=gs.gpu` to `gs.init()` for interactive frame rates.
:::

## Minimal example

The complete script is [`examples/tutorials/advanced_muscle.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/advanced_muscle.py). It drops two spheres (one MPM, one FEM) into a zero-gravity scene and pulses them with a sine wave so you can compare the solvers side by side.

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/muscle.mp4" type="video/mp4">
</video>

Only two things distinguish a soft robot from an ordinary deformable body. First, give the entity a `Muscle` material:

```python
E, nu = 3.0e4, 0.45  # Young's modulus (Pa) and Poisson ratio
rho = 1000.0  # density, kg/m³

robot_mpm = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.5, 0.2, 0.3), radius=0.1),
    material=gs.materials.MPM.Muscle(E=E, nu=nu, rho=rho, model="neohooken"),
)
robot_fem = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.5, -0.2, 0.3), radius=0.1),
    material=gs.materials.FEM.Muscle(E=E, nu=nu, rho=rho, model="stable_neohookean"),
)
```

Second, call `set_actuation` each step instead of a joint-control method:

```python
for i in range(1000):
    actu = [0.2 * (0.5 + np.sin(0.01 * np.pi * i))]  # one value per muscle group
    robot_mpm.set_actuation(actu)
    robot_fem.set_actuation(actu)
    scene.step()
```

Everything else (the plane, the scene, `build`, `step`) is the standard flow from {doc}`/user_guide/getting_started/hello_genesis`.

:::{note}
The constitutive `model` names differ between solvers. MPM uses `"corotation"` or `"neohooken"`; FEM uses `"linear"` or `"stable_neohookean"`. (`"stable_neohooken"` is a deprecated spelling of the FEM model and will warn.)
:::

## The scene: timestep and gravity

Soft-body dynamics need small timesteps and several substeps for numerical stability. Set the timestep on each solver's options, not on `SimOptions`:

```python
dt = 5e-4  # seconds
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        substeps=10,
        gravity=(0, 0, 0),  # float freely so the muscle motion is easy to see
    ),
    mpm_options=gs.options.MPMOptions(
        dt=dt,
        lower_bound=(-1.0, -1.0, -0.2),  # MPM simulates on a fixed grid;
        upper_bound=(1.0, 1.0, 1.0),  # entities must stay inside these bounds
    ),
    fem_options=gs.options.FEMOptions(dt=dt, damping=45.0),
    show_viewer=True,
)
```

The MPM solver discretizes space onto a background grid; `lower_bound` and `upper_bound` set its extent in meters (Z-up). Any particle that leaves the grid is lost, so size the bounds to contain the robot's full range of motion.

## Muscle groups and fiber directions

By default a soft robot has a single muscle group spanning its whole body, with all fibers pointing along `+Z` (`[0, 0, 1]`). A single actuation value then contracts the entire body along that axis: useful for the sphere demo, useless for locomotion.

To make a robot move deliberately, partition it into groups and assign each part a fiber direction. Declare the number of groups on the material, then call `set_muscle` after `build` (it reads the built particle positions):

```python
worm = scene.add_entity(
    morph=gs.morphs.Mesh(
        file="meshes/worm/worm.obj",
        pos=(0.3, 0.3, 0.001),
        scale=0.1,
        euler=(90, 0, 0),  # extrinsic x-y-z, degrees
    ),
    material=gs.materials.MPM.Muscle(
        E=5e5,
        nu=0.45,
        rho=10000.0,
        model="neohooken",
        n_groups=4,  # at most 4 independently actuated muscles
    ),
)

scene.build(n_envs=3)
```

`set_muscle` takes two per-unit arrays, where a *unit* is a particle for MPM and an element for FEM:

- `muscle_group`: an integer in `[0, n_groups)` per unit, naming which muscle each unit belongs to.
- `muscle_direction`: a fiber direction per unit (or one shared vector). Genesis does **not** normalize it; pass unit vectors.

The worm example carves the body into upper/lower and fore/hind quarters by particle position, then points every fiber along `+Y`:

```python
pos = worm.get_state().pos[0]  # ([n_envs,] n_particles, 3) — take env 0
n_units = worm.n_particles  # FEM instead uses worm.n_elements

pos_max, pos_min = pos.max(dim=0).values, pos.min(dim=0).values
pos_range = pos_max - pos_min

lu_thr, fh_thr = 0.3, 0.6
muscle_group = torch.zeros((n_units,), dtype=gs.tc_int, device=gs.device)
mask_upper = pos[:, 2] > (pos_min[2] + pos_range[2] * lu_thr)
mask_fore = pos[:, 1] < (pos_min[1] + pos_range[1] * fh_thr)
muscle_group[mask_upper & mask_fore] = 0  # upper fore body
muscle_group[mask_upper & ~mask_fore] = 1  # upper hind body
muscle_group[~mask_upper & mask_fore] = 2  # lower fore body
muscle_group[~mask_upper & ~mask_fore] = 3  # lower hind body

worm.set_muscle(
    muscle_group=muscle_group,
    muscle_direction=(0.0, 1.0, 0.0),  # fibers along +Y, shared by all units
)
```

`set_actuation` now takes one value per group, so its input has shape `(n_groups,)`. Pulsing only the lower-hind group makes the worm crawl forward:

```python
for i in range(1000):
    actu = (0.0, 0.0, 0.0, 1.0 * (0.5 + math.sin(0.005 * math.pi * i)))  # shape (n_groups,)
    worm.set_actuation(actu)
    scene.step()
```

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/worm.mp4" type="video/mp4">
</video>

The full script is [`examples/tutorials/advanced_worm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/advanced_worm.py).

## Hybrid rigid-soft robots

A hybrid robot drives a soft outer skin with a rigid inner skeleton: the skeleton carries the degrees of freedom, and the skin deforms around it. Build one with `gs.materials.Hybrid`, which pairs a `gs.materials.Rigid` skeleton with a soft material that must be `gs.materials.MPM.Muscle`:

```python
robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="urdf/simple/two_link_arm.urdf",
        pos=(0.5, 0.5, 0.3),
        scale=0.2,
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45, rho=1000.0, model="neohooken"),
        thickness=0.05,  # skin thickness grown around the skeleton, meters
        damping=1000.0,
    ),
)
```

Because the actuation comes from the rigid skeleton, you control a hybrid robot through the ordinary rigid interface (`control_dofs_velocity`, `control_dofs_position`, `control_dofs_force`) with as many values as the skeleton has degrees of freedom:

```python
for i in range(1000):
    dofs_ctrl = [1.0 * np.sin(2 * np.pi * i * 0.001)] * robot.n_dofs
    robot.control_dofs_velocity(dofs_ctrl)  # drive the inner skeleton
    scene.step()
```

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/hybrid_robot.mp4" type="video/mp4">
</video>

The full script is [`examples/tutorials/advanced_hybrid_robot.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/advanced_hybrid_robot.py). See {doc}`hybrid_entity` for how the skin is grown from the skeleton (or the skeleton from a mesh) and how to customize that association.

## See also

- {doc}`hybrid_entity`: building rigid-soft hybrid entities from a URDF or a mesh.
- {doc}`beyond_rigid_bodies`: the MPM, FEM, SPH, and PBD solvers behind fluids, cloth, and deformable bodies.
