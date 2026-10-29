# Deformables and fluids

The {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` tutorial simulated a rigid robot. That same `Scene` can hold water, sand, cloth, and soft tissue at the same time, because Genesis World unifies several physics **solvers** under one scene. A solver is the set of algorithms that advances one family of materials; the class of the entity options you add an entity with decides which solver simulates it.

Choose a solver from the table below, then follow its linked example for the full script.

## Choosing a solver

Every entity is built from entity options, whose class decides the solver, and which carry a `material` stating the physical law the entity follows. In {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` the arm was added from a morph alone, which builds a rigid entity, so the rigid solver handled it. Add an entity with options of another class and its solver runs instead:

| Solver | Representation | Use it when you need | Entity options (`gs.options.*`) | Materials (`gs.materials.*`) |
|---|---|---|---|---|
| **MPM** (Material Point Method) | Hybrid particles + background grid | The widest range of continuum materials in one solver: elastic, plastic, sand, snow | `MPMEntityOptions` | `Elastic`, `Liquid`, `ElastoPlastic`, `Sand`, `Snow`, `Muscle` |
| **FEM** (Finite Element Method) | Tetrahedral mesh | Accurate elasticity and volumetric muscles, where mesh fidelity matters | `FEMEntityOptions` | `Elastic`, `Cloth`, `Muscle` |
| **PBD** (Position-Based Dynamics) | Particles + constraints | Fast cloth, ropes, and topology-preserving deformables | `PBDClothEntityOptions`, `PBDElasticEntityOptions`, `PBDLiquidEntityOptions`, `PBDParticleEntityOptions` | `Cloth`, `Elastic`, `Liquid` |
| **SPH** (Smoothed-Particle Hydrodynamics) | Particles (Lagrangian) | Free-surface liquids driven by real fluid parameters | `SPHEntityOptions` | `Liquid` |

MPM and SPH also power {doc}`particle emitters <emitters>`; MPM and FEM power {doc}`volumetric soft robots <soft_robots>`.

## Setup common to every non-rigid solver

Whichever solver you use, three things change relative to a rigid-only scene.

**1. Enable substepping.** Non-rigid solvers are numerically stiff, so Genesis World subdivides each `scene.step()` into several substeps. Set a small `dt` (in seconds) and a substep count on `SimOptions`; the internal substep is `dt / substeps`. Rigid-only scenes leave `substeps` at its default of `1`.

```python
sim_options=gs.options.SimOptions(
    dt=4e-3,  # seconds
    substeps=10,  # substep_dt = 4e-4 s
)
```

**2. Configure the solver on the scene.** Each solver reads its own options object: `MPMOptions`, `SPHOptions`, `FEMOptions`, `PBDOptions`. Particle-grid solvers (MPM, SPH) require a simulation domain, and the solver clamps entities that leave `lower_bound`/`upper_bound` (in meters, Z-up) to it.

```python
mpm_options=gs.options.MPMOptions(
    lower_bound=(-0.5, -1.0, 0.0),  # meters
    upper_bound=(0.5, 1.0, 1.0),
)
```

**3. Pick the solver, the material, and how it renders.** Choose the class of the entity options to pick the solver, such as {py:class}`gs.options.MPMEntityOptions <genesis.options.entities.MPMEntityOptions>`, give it a material such as {py:class}`gs.materials.Elastic <genesis.options.materials.Elastic>`, and pass a `surface` to control appearance. `vis_mode="particle"` draws the underlying particles; `vis_mode="visual"` deforms the original mesh to follow the internal state (called *skinning* in computer graphics).

```python
obj = scene.add_entity(
    options=gs.options.MPMEntityOptions(
        morph=gs.morphs.Box(
            pos=(0.0, -0.5, 0.25),
            size=(0.2, 0.2, 0.2),
        ),
        surface=gs.surfaces.Default(
            color=(1.0, 0.4, 0.4),
            vis_mode="visual",
        ),
        material=gs.materials.Elastic(
            youngs_modulus=3e5,
        ),
    ),
)
```

## MPM: deformable and granular materials

The Material Point Method carries mass on particles while resolving forces on a background grid, which lets one solver span elastic solids, plastics, sand, and snow. Use MPM when a scene needs several continuum behaviors at once, or a material that flows and then holds its deformed shape.

Only the `material` differs between an elastic cube, a liquid cube, and an elastoplastic sphere:

```python
scene.add_entity(options=gs.options.MPMEntityOptions(material=gs.materials.Elastic(youngs_modulus=3e5), ...))
scene.add_entity(options=gs.options.MPMEntityOptions(material=gs.materials.Liquid(), ...))
scene.add_entity(options=gs.options.MPMEntityOptions(material=gs.materials.ElastoPlastic(), ...))
```

Full script: [`examples/tutorials/mpm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/mpm.py).

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/mpm.mp4" type="video/mp4">
Three MPM objects falling and deforming: an elastic cube, a liquid cube, and an elastoplastic sphere.
</video>

## FEM: accurate elasticity and muscles

The Finite Element Method discretizes an entity into a tetrahedral mesh and solves the elasticity equations on it. Choose FEM over MPM when mesh-level accuracy matters: stiff elastic bodies, volumetric muscles, and contact-rich soft-body manipulation. Under {py:class}`gs.options.FEMEntityOptions <genesis.options.entities.FEMEntityOptions>`, an `Elastic` material exposes the physical parameters directly, such as Young's modulus `youngs_modulus` (Pa) and Poisson ratio `poisson_ratio`.

FEM underpins the {doc}`soft robots tutorial <soft_robots>`, which actuates a volumetric muscle. FEM entities also couple to rigid arms for grasping; see [`examples/coupling/fem_cube_linked_with_arm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/fem_cube_linked_with_arm.py).

## PBD: cloth and topology-preserving deformables

Position-Based Dynamics represents an entity as particles linked by constraints and solves for positions directly, which makes it fast and stable for cloth, ropes, and other 1D/2D/3D bodies that keep their topology. {py:class}`gs.options.PBDClothEntityOptions <genesis.options.entities.PBDClothEntityOptions>` loads a 2D mesh as a sheet of {py:class}`gs.materials.Cloth <genesis.options.materials.Cloth>`.

You can pin individual particles after building. `find_closest_particle` locates the particle nearest a world-space point (meters), and `fix_particles` anchors it:

```python
scene.build()

# pin all four corners of the sheet in place
cloth.fix_particles(cloth.find_closest_particle((-1, -1, 1.0)))
cloth.fix_particles(cloth.find_closest_particle((1, 1, 1.0)))
```

Full script: [`examples/tutorials/pbd_cloth.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/pbd_cloth.py).

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/pbd_cloth.mp4" type="video/mp4">
Two PBD cloth sheets: one pinned at four corners, a second dropping onto it pinned at one corner.
</video>

:::{warning}
Skinning a flat 2D cloth mesh with `vis_mode="visual"` can produce degenerate barycentric weights, which shows up as distorted rendering, especially with a non-zero `euler`. Use `vis_mode="particle"` for flat sheets until this is resolved.
:::

## SPH: free-surface liquids

Smoothed-Particle Hydrodynamics is a purely Lagrangian (particle-only) solver aimed at liquids. Use SPH when you want fluid governed by physical parameters (rest density `density` in kg/m³, `viscosity`, and `surface_tension` of {py:class}`gs.materials.Liquid <genesis.options.materials.Liquid>`) rather than the coarser liquid model MPM provides.

Turning a rigid block into water takes one change: add it with {py:class}`gs.options.SPHEntityOptions <genesis.options.entities.SPHEntityOptions>`, whose material defaults to `gs.materials.Liquid()`. Tune the flow with the parameters of the material:

```python
liquid = scene.add_entity(
    options=gs.options.SPHEntityOptions(
        morph=gs.morphs.Box(
            pos=(0.0, 0.0, 0.65),
            size=(0.4, 0.4, 0.4),
        ),
        surface=gs.surfaces.Default(
            color=(0.4, 0.8, 1.0),
            vis_mode="particle",
        ),
        material=gs.materials.Liquid(),  # or Liquid(viscosity=0.02, surface_tension=0.02) for a thicker fluid
    ),
)
```

Read live particle positions with `liquid.get_particles_pos()`, which returns a tensor of shape `([n_envs,] n_particles, 3)` in meters.

Full script: [`examples/tutorials/sph_liquid.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/sph_liquid.py).

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/sph_liquid.mp4" type="video/mp4">
An SPH liquid block collapsing and spreading across the ground, contained within the solver boundary.
</video>

:::{note}
{py:class}`gs.options.SPHEntitySolverOptions <genesis.options.entities.SPHEntitySolverOptions>` accepts a `sampler` that controls how particles fill the morph: `"regular"` (a grid lattice, the SPH default for numerical stability), `"pbs"` (physics-based sampling, which runs extra steps for a natural arrangement), or `"random"`.
:::

## SF: gaseous phenomena (smoke)

The Stable Fluid solver works on a fixed 3D grid (Eulerian): it advects a velocity field and one or more scalar density fields, then makes the velocity divergence-free with a Jacobi pressure projection. Use it for smoke and other gases, and set the grid resolution with `SFOptions.res`.

SF has no Lagrangian entity you add and move: gas enters through velocity **jets** you register on the solver, and the solver stays inactive until at least one jet exists. Each substep advects the velocity and density fields (RK3 backtracing with trilinear interpolation), injects momentum at the jets, then runs `solver_iters` Jacobi pressure iterations to keep the velocity divergence-free. State lives on the fixed grid, so there are no per-entity get/set methods, and SF does not participate in checkpointing. Read the density grid back for rendering.

Full script, including the jet class and writing the density field to images: [`examples/fluid/smoke.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/fluid/smoke.py).

## See also

- {doc}`Muscle actuation <soft_robots>`: actuate MPM and FEM muscles.
- {doc}`Hybrid entities <hybrid_entity>`: couple a rigid skeleton to a soft skin.
- {doc}`Particle emitters <emitters>`: stream MPM, SPH, or PBD particles into a scene.
- {doc}`Solvers and coupling </user_guide/physics/coupling/index>`: how solvers exchange forces across material boundaries. Runnable pairings live in [`examples/coupling`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/coupling), and the IPC contact solver for stiff soft-body contact in [`examples/ipc`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/ipc).

```{toctree}
:hidden:
:maxdepth: 1

soft_robots
hybrid_entity
```
