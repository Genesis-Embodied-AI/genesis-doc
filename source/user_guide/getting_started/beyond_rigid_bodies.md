# 🌊 Beyond Rigid Bodies

Genesis unified multiple physics solvers and supports simulation beyond rigid body dynamics. A `solver` is essentially a set of physics simulation algorithms to handle a specific set of materials. In this tutorial, we will go through 3 popular solvers and use them to simulate entities with different physical properties:
- [Smooth Particle Hydrodynamics (SPH) Solver](#sph)
- [Material Point Method (MPM) Solver](#mpm)
- [Position Based Dynamics (PBD) Solver](#pbd)

## Liquid simulation using SPH Solver <a id="sph"></a>
First, let's see how we can simulate a water cube. Let's create an empty scene and add a plane as usual:
```python
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################

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

########################## entities ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)
```
A few things to we should pay attention to here:
- When configuring `sim_options`, now we are using a relatively small `dt` with `substeps=10`. This means inside the simulator, for each `step`, it will simulate 10 `substep`s, each with `substep_dt = 4e-3 / 10`. When we were dealing with rigid bodies earlier, we didn't need to set this and simply used the default setting (`substeps=1`), which only runs 1 substeps in each step.
Next, let's add water. Adding
- As we discussed before, we use `options` to configure each different solver. Since we are using `SPHSolver`, we need to configure its properties via `sph_options`. In this example, we set the boundary of the solver, and specified the particle size to be 0.01m. SPHSolver is a lagrangian solver, meaning it uses particles to represent objects.
- In `vis_options`, we specified that we would like to see the boundary of the SPH Solver in the rendered view.

Next, let's add a water block entity and start the simulation!
When we add the block, the only difference we need to make to turn it from a rigid block to a water block is setting the `material`. In fact, earlier when we were dealing with only rigid bodies, this was internally set to be `gs.materials.Rigid()` by default. Since we are now using the SPH Solver for liquid simulation, we select the `Liquid` material under the `SPH` category:
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

########################## build ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()
```
When creating the `Liquid` material, we set `sampler='pbs'`. This configures how we want to sample particles given the `Box` morph. `pbs` stands for 'physics-based sampling', which runs some extra simulation steps to make sure the particles are arranged in a physically natural way. You can also use `'regular'` sampler to sample the particles simply using a grid lattice pattern. If you are using other solvers such as MPM, you can also use `'random'` sampler.

You may also note that we passed in an extra attribute -- `surface`. This attribute is used to define all the visual properties of the entity. Here, we set the color of the water to be blueish, and chose to visualize it as particles by setting `vis_mod='particle'`.

Once you run this successfully, you will see the water drops and spreads over the plane, but constrained within the solver boundary:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/sph_liquid.mp4" type="video/mp4">
</video>

You can get the real-time particle positions by:
```
particles = liquid.get_particles_pos()
```

**Changing the liquid properties:** You can also play with the physical properties of the liquid. For example, you can increase its viscosity (`mu`) and surface tension (`gamma`):
```python
material=gs.materials.SPH.Liquid(mu=0.02, gamma=0.02),
```
and see how the behavior will be different. Enjoy!

The complete script:
```python
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################

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

########################## entities ##########################
plane = scene.add_entity(
    morph=gs.morphs.Plane(),
)

liquid = scene.add_entity(
    # viscous liquid
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

########################## build ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()

# get particle positions
particles = liquid.get_particles_pos()
```

## Deformable object simulation using MPM Solver <a id="mpm"></a>

MPM solver is a very powerful physics solver that supports a wider range of materials. MPM stands for material point method, and uses a hybrid lagrangian-eulerian representation, i.e. both particles and grids, to represent objects.

In this example, let's create three objects:
- An elastic cube, visualized as `'particles'`
- A liquid cube, visualized as `'particles'`
- An elastoplastic sphere, visualized as the original sphere mesh, but deformed based on the internal particle state (`vis_mode='visual'`). Such process that maps internal particle state to a deformed visual mesh is called *skinning* in computer graphics.

Complete code script:
```python
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################

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

########################## entities ##########################
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


########################## build ##########################
scene.build()

horizon = 1000
for i in range(horizon):
    scene.step()
```
Note that to change the underlying physical material, all you have to do is to change the `material` attribute. Feel free to play with other material types (such as `MPM.Sand()` and `MPM.Snow()`), as well as the property values in each material type.

Expected rendered result:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/mpm.mp4" type="video/mp4">
</video>

## Cloth simulation with PBD Solver <a id="pbd"></a>

PBD stands for Position Based Dynamics. This is also a lagrangian solver that represents entities using particles and edges, and simulates their state by solving a set of position-based constraints. It can be used to simulate 1D/2D/3D entities that preserve their topologies. In this example, we will see how to simulate cloth with PBD solver.

In this example, we will add two square-shape cloth entities: one with 4 corners fixed, the other with only 1 corner fixed and falls down onto the first piece of cloth. In addition, we will render them using different `vis_mode`s.

Create the scene and build:
```python
import genesis as gs

########################## init ##########################
gs.init()

########################## create a scene ##########################

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

########################## entities ##########################
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

########################## build ##########################
scene.build()
```

Then, let's fix the corners (particles) we want. To do this, we provide a handy tool to locate a particle using a location in the cartesian space:
```python

cloth_1.fix_particles(cloth_1.find_closest_particle((-1, -1, 1.0)))
cloth_1.fix_particles(cloth_1.find_closest_particle((1, 1, 1.0)))
cloth_1.fix_particles(cloth_1.find_closest_particle((-1, 1, 1.0)))
cloth_1.fix_particles(cloth_1.find_closest_particle((1, -1, 1.0)))
cloth_2.fix_particles(cloth_2.find_closest_particle((-1, -1, 1.0)))

horizon = 1000
for i in range(horizon):
    scene.step()
```

Expected rendered result:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/pbd_cloth.mp4" type="video/mp4">
</video>


:::{warning}
**Skinning for 2D meshes**

We noticed some issues when using a 2D flat cloth mesh and set `vis_mode='visual'`, this is due to degenerated pseudo-inverse matrix computation when computing the barycentric weights. You may notice weird visualization results in the above example if you add a non-zero euler to the cloth and use `vis_mode='visual'`. We will fix this very soon.
:::

***More tutorials on inter-solver coupling coming soon!***