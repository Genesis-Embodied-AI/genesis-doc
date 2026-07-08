# Beyond rigid bodies

The {doc}`Hello, Genesis World <hello_genesis>` tutorial simulated a rigid robot. But a scene can hold water, sand, cloth, and soft tissue at the same time, because Genesis World unifies several physics **solvers** under one `Scene`. A solver is the set of algorithms that advances one family of materials; the material you assign to an entity decides which solver simulates it.

This page introduces the non-rigid solvers, explains when to reach for each, and links a runnable example per solver. It is an overview: read it to choose a solver, then follow the linked example for the full script.

## Choosing a solver

Every entity carries a `material`. In {doc}`Hello, Genesis World <hello_genesis>` the material defaulted to `gs.materials.Rigid()`, so the rigid solver handled the arm. Assign a material from a different family and its solver runs instead:

| Solver | Representation | Reach for it when you need | Materials (`gs.materials.<S>.*`) |
|---|---|---|---|
| **MPM** (Material Point Method) | Hybrid particles + background grid | The widest range of continuum materials in one solver: elastic, plastic, sand, snow | `Elastic`, `Liquid`, `ElastoPlastic`, `Sand`, `Snow`, `Muscle` |
| **FEM** (Finite Element Method) | Tetrahedral mesh | Accurate elasticity and volumetric muscles, where mesh fidelity matters | `Elastic`, `Cloth`, `Muscle` |
| **PBD** (Position-Based Dynamics) | Particles + constraints | Fast cloth, ropes, and topology-preserving deformables | `Cloth`, `Elastic`, `Liquid`, `Particle` |
| **SPH** (Smoothed-Particle Hydrodynamics) | Particles (Lagrangian) | Free-surface liquids driven by real fluid parameters | `Liquid` |

MPM and SPH also power {doc}`particle emitters <emitters>`; MPM and FEM power {doc}`volumetric soft robots <soft_robots>`.

## The pattern shared by every non-rigid solver

Whichever solver you use, three things change relative to a rigid-only scene.

**1. Enable substepping.** Non-rigid solvers are numerically stiff, so each `scene.step()` is subdivided into several substeps. Set a small `dt` (in seconds) and a substep count on `SimOptions`; the internal substep is `dt / substeps`. Rigid-only scenes leave `substeps` at its default of `1`.

```python
sim_options=gs.options.SimOptions(
    dt=4e-3,  # seconds
    substeps=10,  # substep_dt = 4e-4 s
)
```

**2. Configure the solver on the scene.** Each solver reads its own options object: `MPMOptions`, `SPHOptions`, `FEMOptions`, `PBDOptions`. Particle-grid solvers (MPM, SPH) require a simulation domain; entities that leave `lower_bound`/`upper_bound` (in meters, Z-up) are clamped to it.

```python
mpm_options=gs.options.MPMOptions(
    lower_bound=(-0.5, -1.0, 0.0),  # meters
    upper_bound=(0.5, 1.0, 1.0),
)
```

**3. Set the material and how it renders.** Swap the entity's `material` to pick the solver, and pass a `surface` to control appearance. `vis_mode="particle"` draws the underlying particles; `vis_mode="visual"` deforms the original mesh to follow the internal state (called *skinning* in computer graphics).

```python
obj = scene.add_entity(
    material=gs.materials.MPM.Elastic(),
    morph=gs.morphs.Box(pos=(0.0, -0.5, 0.25), size=(0.2, 0.2, 0.2)),
    surface=gs.surfaces.Default(color=(1.0, 0.4, 0.4), vis_mode="visual"),
)
```

## MPM: deformable and granular materials

The Material Point Method carries mass on particles while resolving forces on a background grid, which lets one solver span elastic solids, plastics, sand, and snow. Reach for MPM when you want several continuum behaviors in the same scene, or a material that flows and then holds its deformed shape.

Only the `material` differs between an elastic cube, a liquid cube, and an elastoplastic sphere:

```python
scene.add_entity(material=gs.materials.MPM.Elastic(), ...)
scene.add_entity(material=gs.materials.MPM.Liquid(), ...)
scene.add_entity(material=gs.materials.MPM.ElastoPlastic(), ...)
```

Full script: [`examples/tutorials/mpm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/mpm.py).

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/mpm.mp4" type="video/mp4">
Three MPM objects falling and deforming: an elastic cube, a liquid cube, and an elastoplastic sphere.
</video>

## FEM: accurate elasticity and muscles

The Finite Element Method discretizes an entity into a tetrahedral mesh and solves the elasticity equations on it. Choose FEM over MPM when mesh-level accuracy matters: stiff elastic bodies, volumetric muscles, and contact-rich soft-body manipulation. `gs.materials.FEM.Elastic` exposes the physical parameters directly, such as Young's modulus `E` (Pa) and Poisson ratio `nu`.

FEM underpins the {doc}`soft robots tutorial <soft_robots>`, which actuates a volumetric muscle. FEM entities also couple to rigid arms for grasping; see [`examples/coupling/fem_cube_linked_with_arm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/fem_cube_linked_with_arm.py).

## PBD: cloth and topology-preserving deformables

Position-Based Dynamics represents an entity as particles linked by constraints and solves for positions directly, which makes it fast and stable for cloth, ropes, and other 1D/2D/3D bodies that keep their topology. `gs.materials.PBD.Cloth` loads a 2D mesh as a sheet.

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

Smoothed-Particle Hydrodynamics is a purely Lagrangian (particle-only) solver aimed at liquids. Reach for SPH when you want fluid governed by physical parameters — rest density `rho` (kg/m³), viscosity `mu`, and surface tension `gamma` — rather than the coarser liquid model MPM provides.

Turning a rigid block into water is one line: give it an SPH liquid material. Tune the flow with its parameters:

```python
liquid = scene.add_entity(
    material=gs.materials.SPH.Liquid(),  # or Liquid(mu=0.02, gamma=0.02) for a thicker fluid
    morph=gs.morphs.Box(pos=(0.0, 0.0, 0.65), size=(0.4, 0.4, 0.4)),
    surface=gs.surfaces.Default(color=(0.4, 0.8, 1.0), vis_mode="particle"),
)
```

Read live particle positions with `liquid.get_particles_pos()`, which returns a tensor of shape `([n_envs,] n_particles, 3)` in meters.

Full script: [`examples/tutorials/sph_liquid.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/tutorials/sph_liquid.py).

<video preload="auto" controls="True" width="100%">
<source src="../../_static/videos/sph_liquid.mp4" type="video/mp4">
An SPH liquid block collapsing and spreading across the ground, contained within the solver boundary.
</video>

:::{note}
The `Liquid` material accepts a `sampler` that controls how particles fill the morph: `"regular"` (a grid lattice, the SPH default for numerical stability), `"pbs"` (physics-based sampling, which runs extra steps for a natural arrangement), or `"random"`.
:::

## Next steps

- {doc}`Soft robots <soft_robots>`: actuate MPM and FEM muscles.
- {doc}`Hybrid entities <hybrid_entity>`: couple a rigid skeleton to a soft skin.
- {doc}`Particle emitters <emitters>`: stream MPM, SPH, or PBD particles into a scene.
- {doc}`Solvers and coupling </user_guide/advanced_topics/solvers_and_coupling>`: how solvers exchange forces across material boundaries. Runnable pairings live in [`examples/coupling`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/coupling), and the IPC contact solver for stiff soft-body contact in [`examples/IPC_Solver`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/IPC_Solver).
