# 🗂 Config System

## Overview

The Genesis simulation framework is built around a modular and extensible configuration system. This system allows users to flexibly compose and control different aspects of a simulation—ranging from low-level physics solvers to high-level rendering options—through structured configuration objects.

To help you understand how these components work together, we start with a high-level template of how a Genesis scene is typically initialized. This template shows how simulation settings, solver options, and entity-level configurations are orchestrated.

```python
# Initializate Genesis
gs.init(...)

# Initialize scene
scene = gs.Scene(
    # simulation & coupling
    sim_options=SimOptions(...),
    coupler_options=CouplerOptions(...),

    # solvers
    tool_options=ToolOptions(...),
    rigid_options=RigidOptions(...),
    avatar_options=AvatarOptions(...),
    mpm_options=MPMOptions(...),
    sph_options=SPHOptions(...),
    fem_options=FEMOptions(...),
    sf_options=SFOptions(...),
    pbd_options=PBDOptions(...),

    # visualization & rendering
    vis_options=VisOptions(...),
    viewer_options=ViewerOptions(...),
    renderer=Rasterizer(...),
)

# Add entities
scene.add_entity(
    morph=gs.morphs...,
    material=gs.materials...,
    surface=gs.surfaces....,
)
```

As shown above, a scene in Genesis is defined by a combination of:

- [Simulation & Coupling](#simulation--coupling): Defines global simulation parameters and how different solvers interact.
- [Solvers](#solvers): Configure physical behaviors for different simulation methods (e.g., rigid bodies, fluids, cloth).
- [Visualization & Rendering](#visualization--rendering): Customize runtime visualization and final rendering options.
- For each entity added to the scene:
    - [Morph](#morph): Defines the geometry or structure of the entity.
    - [Material](#material): Specifies material properties relevant with the corresponding physics solver.
    - [Surface](#surface): Controls visual appearance and surface rendering.

## Simulation & Coupling

This configuration defines how the simulation is globally structured and how different physics solvers are coupled. These options control the "skeleton" of the simulation loop, e.g., time-stepping, stability, and solver interoperability.

- `SimOptions`: Sets global simulation parameters—time step size, gravity, damping, and numerical integrator.
- `CouplerOptions`: Configures multi-physics interactions - for instance, how a rigid tool interacts with a soft deformable body or how a fluid flows through a porous material.

Defined in [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py).

## Solvers

Solvers are the cores behind specific physical models. Each solver encapsulates a simulation algorithm for a particular material or system—rigid bodies, fluids, deformables, etc. Users can enable or disable solvers depending on the scenario.
- `RigidOptions`: Rigid body dynamics with contact, collision, and constraints.
- `AvatarOptions`: Simulation of animated characters.
- `MPMOptions`: Material Point Method solver for elastic, plastic, granular, fluidic materials.
- `SPHOptions`: Smoothed Particle Hydrodynamics solver for fluids and granular flows.
- `FEMOptions`: Finite Element Method solver for elastic material.
- `SFOptions`: Stable Fluid solver for eulerian-based gaseous simulation.
- `PBDOptions`: Position-Based Dynamics solver for cloth, volumetric deformable objects, liquid, and particles.
- `ToolOptions`: A temporary setup. To be deprecated.

Defined in [genesis/options/solvers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/solvers.py).

## Visualization & Rendering

This configuration controls both the live visualization (useful during debugging and development) and the final rendered output (useful for demos, analysis, or media). It governs how users interact with and perceive the simulation visually.
- `ViewerOptions`: Configure properties of the interactive viewer.
- `VisOptions`: Configure visualization-related properties that are independent of the viewer or camera.
- `Renderer` (Rasterizer or Raytracer): Defines the rendering backend, including lighting, shading, and post-processing effects. Support Rasterization or Raytracing.

Defined in [genesis/options/vis.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/vis.py) and [genesis/options/renderers.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/renderers.py).

## Morph

Morphs define the shape and topology of an entity. This includes primitive geometries (e.g., spheres, boxes), structured assets (e.g., articulated arms). Morphs form the geometric foundation on which materials and physics operate.
- `Primitive`: For all shape-primitive morphs.
    - `Box`: Morph defined by a box shape.
    - `Cylinder`: Morph defined by a cylinder shape.
    - `Sphere`: Morph defined by a sphere shape.
    - `Plane`: Morph defined by a plane shape.
- `FileMorph`:
    - `Mesh`: Morph loaded from a mesh file.
        - `MeshSet`: A collection of meshes.
    - `MJCF`: Morph loaded from a MJCF file. This morph only supports rigid entity.
    - `URDF`: Morph loaded from a URDF file. This morph only supports rigid entity.
    - `Drone`: Morph loaded from a URDF file for creating a drone entity.
- `Terrain`: Morph for creating a rigid terrain.
- `NoWhere`: Reserved for emitter. Internal use only.

Defined in [genesis/options/morphs.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/morphs.py).

## Material

Materials define how an object responds to physical forces. This includes stiffness, friction, elasticity, damping, and solver-specific material parameters. The material also determines how an entity interacts with other objects and solvers.
- `Rigid`: Rigid-bodied and articulated.
    - `Avatar`: Abstraction for avatar / animated characters.
- `MPM`: Material Point Method.
    - `Elastic`
    - `ElastoPlastic`
    - `Liquid`
    - `Muscle`
    - `Sand`
    - `Snow`
- `FEM`: Finite Element Method.
    - `Elastic`
    - `Muscle`
- `PBD`: Position Based Dynamics.
    - `Cloth`
    - `Elastic`
    - `Liquid`
    - `Particle`
- `SF`: Stable Fluid.
    - `Smoke`
- `Hybrid`: Rigid skeleton actuating soft skin.
- `Tool`: Temporary and to be deprecated.

These can be found in [genesis/engine/materials](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/engine/materials).

## Surface

Surfaces define how an entity appears visually. They include rendering properties like color, texture, reflectance, transparency, and more. Surfaces are the interface between an entity's internal structure and the renderer.

- `Default`: Basically `Plastic`.
- `Plastic`: Plastic surface is the most basic type of surface.
    - `Rough`: Shortcut for a rough surface with proper parameters.
    - `Smooth`: Shortcut for a smooth surface with proper parameters.
    - `Reflective`: For collision geometry with a grey color by default.
    - `Collision`: Shortcut for a rough plastic surface with proper parameters.
- `Metal`
    - `Iron`: Shortcut for an metallic surface with `metal_type = 'iron'`.
    - `Aluminium`: Shortcut for an metallic surface with `metal_type = 'aluminium'`.
    - `Copper`: Shortcut for an metallic surface with `metal_type = 'copper'`.
    - `Gold`: Shortcut for an metallic surface with `metal_type = 'gold'`.
- `Glass`
    - `Water`: Shortcut for a water surface (using Glass surface with proper values).
- `Emission`: Emission surface. This surface emits light.

Defined in [genesis/options/surfaces.py](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/genesis/options/surfaces.py).
