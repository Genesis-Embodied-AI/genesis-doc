# Deformables and fluids

The {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` tutorial simulated a rigid robot. That same `Scene` can hold water, sand, cloth, and soft tissue at the same time, because Genesis World unifies several physics **solvers** under one scene. A solver is the set of algorithms that advances one family of materials; the material you assign to an entity decides which solver simulates it.

Choose a solver from the table below, then follow its linked example for the full script.

## Choosing a solver

Every entity carries a `material`. In {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>` the material defaulted to `gs.materials.Rigid()`, so the rigid solver handled the arm. Assign a material from a different family and its solver runs instead:

| Solver | Representation | Use it when you need | Materials (`gs.materials.<S>.*`) |
|---|---|---|---|
| **MPM** (Material Point Method) | Hybrid particles + background grid | The widest range of continuum materials in one solver: elastic, plastic, sand, snow | `Elastic`, `Liquid`, `ElastoPlastic`, `Sand`, `Snow`, `Muscle` |
| **FEM** (Finite Element Method) | Tetrahedral mesh | Accurate elasticity and volumetric muscles, where mesh fidelity matters | `Elastic`, `Cloth`, `Muscle` |
| **PBD** (Position-Based Dynamics) | Particles + constraints | Fast cloth, ropes, and topology-preserving deformables | `Cloth`, `Elastic`, `Liquid`, `Particle` |
| **SPH** (Smoothed-Particle Hydrodynamics) | Particles (Lagrangian) | Free-surface liquids driven by real fluid parameters | `Liquid` |

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

**3. Set the material and how it renders.** Swap the entity's `material` to pick the solver, and pass a `surface` to control appearance. The material decides what the surface is drawn on: a solid deforms its original mesh to follow the internal state (called *skinning* in computer graphics), and a liquid or granular material draws a surface reconstructed from its particles. To draw the underlying particles instead, set `vis=gs.options.EntityVisOptions(debug=True)` on the entity spec, or switch the whole scene to the {ref}`debug view <debug-view>`.

```python
obj = scene.add_entity(
    material=gs.materials.MPM.Elastic(),
    morph=gs.morphs.Box(pos=(0.0, -0.5, 0.25), size=(0.2, 0.2, 0.2)),
    surface=gs.surfaces.Default(color=(1.0, 0.4, 0.4)),
)
```

## MPM: deformable and granular materials

The Material Point Method carries mass on particles while resolving forces on a background grid, which lets one solver span elastic solids, plastics, sand, and snow. Use MPM when a scene needs several continuum behaviors at once, or a material that flows and then holds its deformed shape.

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

The Finite Element Method discretizes an entity into a tetrahedral mesh and solves the elasticity equations on it. Choose FEM over MPM when mesh-level accuracy matters: stiff elastic bodies, volumetric muscles, and contact-rich soft-body manipulation. {py:class}`gs.materials.FEM.Elastic <genesis.engine.materials.FEM.elastic.Elastic>` exposes the physical parameters directly, such as Young's modulus `E` (Pa) and Poisson ratio `nu`.

To hold some vertices of an FEM entity in place, such as a soft pad clamped by one face, build the entity from an entity spec, {py:class}`gs.entities.FEM <genesis.options.entities.FEM>`, and select the vertices on it. `gs.indices.Vertex.in_box` and `gs.indices.Vertex.closest_to` take positions in the frame of the morph, relative to its `pos`:

```python
pad_spec = gs.entities.FEM(
    morph=gs.morphs.Box(pos=(0.0, 0.0, 0.5), size=(0.2, 0.2, 0.2)),
    material=gs.materials.FEM.Elastic(E=1.0e5, nu=0.45),
)
# Clamp the top face: the box spans -0.1 to 0.1 in the frame of its morph
pad_spec.select(gs.indices.Vertex.in_box((-0.1, -0.1, 0.099), (0.1, 0.1, 0.1))).set_is_fixed(True)
pad = scene.add_entity(spec=pad_spec)
```

The fixed vertices become vertex constraints at build, which `pad.remove_vertex_constraints()` releases. [`examples/deformable/fem_hard_and_soft_constraint.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/deformable/fem_hard_and_soft_constraint.py) fixes vertices by box and by closest point.

FEM underpins the {doc}`soft robots tutorial <soft_robots>`, which actuates a volumetric muscle. FEM entities also couple to rigid arms for grasping; see [`examples/coupling/fem_cube_linked_with_arm.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/fem_cube_linked_with_arm.py).

## PBD: cloth and topology-preserving deformables

Position-Based Dynamics represents an entity as particles linked by constraints and solves for positions directly, which makes it fast and stable for cloth, ropes, and other 1D/2D/3D bodies that keep their topology. {py:class}`gs.materials.PBD.Cloth <genesis.engine.materials.PBD.cloth.Cloth>` loads a 2D mesh as a sheet.

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
Skinning a flat 2D cloth mesh can produce degenerate barycentric weights, which shows up as distorted rendering, especially with a non-zero `euler`. Draw flat sheets as their particles in the viewer, with `vis=gs.options.EntityVisOptions(debug=True)` on the entity spec, until this is resolved.
:::

## SPH: free-surface liquids

Smoothed-Particle Hydrodynamics is a purely Lagrangian (particle-only) solver aimed at liquids. Use SPH when you want fluid governed by physical parameters (rest density `rho` in kg/m³, viscosity `mu`, and surface tension `surface_tension` in N/m) rather than the coarser liquid model MPM provides.

Turning a rigid block into water is one line: give it an SPH liquid material. Tune the flow with its parameters:

```python
liquid = scene.add_entity(
    material=gs.materials.SPH.Liquid(),  # or Liquid(mu=0.02) for a thicker fluid
    morph=gs.morphs.Box(pos=(0.0, 0.0, 0.65), size=(0.4, 0.4, 0.4)),
    surface=gs.surfaces.Default(color=(0.4, 0.8, 1.0)),
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
