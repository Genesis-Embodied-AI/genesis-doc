# Force fields

A force field applies a spatially varying acceleration to the particles of an entity every substep. Use one to push a fluid with wind, swirl a liquid into a vortex, add drag, or drive turbulence, without scripting per-particle forces yourself.

Despite the name, a force field is an **acceleration field**: it contributes an acceleration in m/s², not a force in newtons. Acceleration is the physically meaningful quantity here, because force has no notion of spatial density and a field returns a value at every point in space. Genesis World integrates the acceleration into each affected particle's velocity as `vel += acc * substep_dt`.

Force fields act only on **particle-based entities** stepped by the PBD and SPH solvers (fluids, cloth, and other particle materials). They do not affect rigid bodies, MPM, or FEM entities. To apply a world force to a rigid body, use its entity API instead.

:::{note}
No runnable example ships for this feature yet, so the snippet below is illustrative. Every symbol and argument in it is taken from the live API (`gs.force_fields`) and the {doc}`Force field API </api_reference/scene/force_field>`, but the script has not been added to `examples/`.
:::

## Minimal example

Add a field to a scene, activate it, build, and step. Here a constant crosswind blows a column of SPH liquid sideways as it falls:

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
    sph_options=gs.options.SPHOptions(
        lower_bound=(-0.5, -0.5, 0.0),
        upper_bound=(0.5, 0.5, 1.0),
        particle_size=0.01,
    ),
    show_viewer=True,
)

scene.add_entity(gs.morphs.Plane())
liquid = scene.add_entity(
    material=gs.materials.SPH.Liquid(),
    morph=gs.morphs.Box(pos=(0.0, 0.0, 0.65), size=(0.4, 0.4, 0.4)),
)

# Instantiate, then register with the scene *before* building.
wind = gs.force_fields.Constant(direction=(1, 0, 0), strength=5.0)  # 5 m/s2 along +X
scene.add_force_field(wind)

scene.build()

wind.activate()  # fields start inactive; turn it on to apply acceleration
for i in range(1000):
    scene.step()
```

## The lifecycle

A force field goes through four stages. Getting the order right matters: adding after `build()` or forgetting to activate are the two most common mistakes.

1. **Instantiate** a field from `gs.force_fields.*`, passing its parameters:

   ```python
   wind = gs.force_fields.Constant(direction=(1, 0, 0), strength=5.0)
   ```

2. **Register** it with the scene using `scene.add_force_field(field)`, which returns the same field. This must happen **before** `scene.build()`: the number of registered fields is baked into the compiled solver kernels, so a field added afterward is never evaluated.

3. **Activate** it with `field.activate()`. A field is inactive when created (`field.active` is `False`) and contributes zero acceleration until activated. You can toggle `activate()` and `deactivate()` at any time after building, including mid-simulation, and read `field.active` to check the current state.

4. **Step** the scene. On each substep the active field's acceleration is added to every affected particle.

## Available field types

All fields subclass `gs.force_fields.ForceField` and return an acceleration in m/s². Unless noted, a positive `strength` scales the effect and vectors follow the right-handed, Z-up frame.

| Field | Effect | Key parameters |
|---|---|---|
| `Constant` | Uniform acceleration everywhere, like a steady gravity or wind. | `direction` (normalized), `strength` (m/s²) |
| `Wind` | Constant acceleration, but only inside an infinite cylinder; zero outside. | `direction` (cylinder axis, normalized), `strength` (m/s²), `radius` (m), `center` (m) |
| `Point` | Attracts particles toward a point or repels them, set by the sign of `strength`, with distance falloff. | `strength` (m/s²), `position` (m), `falloff_pow`, `flow` |
| `Drag` | Acceleration opposing velocity, combining a linear and a quadratic term. | `linear` (1/s), `quadratic` (1/m) |
| `Noise` | Independent random acceleration per particle per step, uniform in `[-strength, strength]` on each axis. | `strength` (m/s²) |
| `Vortex` | Swirls particles around an axis with tangential and radial components, with distance falloff. | `direction` (axis), `center` (m), `strength_perpendicular` (+ counterclockwise), `strength_radial` (+ inward), `falloff_pow`, `falloff_min` (m), `falloff_max` (m), `damping` |
| `Turbulence` | Smoothly varying acceleration sampled from 3D Perlin noise. | `strength` (m/s²), `frequency` (spatial), `flow`, `seed` |
| `Custom` | Your own acceleration function of position, velocity, time, and particle index. | `func` |

For `Custom`, `func` is a Quadrants kernel function (a Python callable wrapped with `@qd.func`) with the signature `f(pos, vel, t, i) -> vec3`, returning the acceleration in m/s²:

```python
import quadrants as qd


@qd.func
def swirl(pos, vel, t, i):
    return qd.Vector([-pos[1], pos[0], 0.0], dt=gs.qd_float)  # m/s2


scene.add_force_field(gs.force_fields.Custom(swirl))
```

`Turbulence` is built from `gs.force_fields.PerlinNoiseField`, a standalone 3D Perlin noise generator (parameters `wrap_size`, `frequency`, `seed`, `seed_offset`). You rarely construct it directly; reach for it only when writing a `Custom` field that needs coherent noise.

## Notes and gotchas

:::{warning}
**Register before building.** `scene.add_force_field(...)` must be called before `scene.build()`. The active-field count is compiled into the solver kernels, so a field added after building is silently ignored.
:::

- **It is acceleration, not force.** The value is in m/s² and is independent of particle mass, so heavy and light particles gain the same velocity per step. Multiply by mass yourself if you are reasoning about forces.
- **Only PBD and SPH particles are affected.** Rigid bodies, MPM, and FEM entities ignore force fields entirely. Add a particle-based entity (an SPH liquid, a PBD cloth or fluid) for the field to have anything to act on.
- **Fields stack.** Every active field is summed, so you can combine, for example, a `Constant` gravity offset with a `Drag` term and a `Turbulence` gust.
- **Activation is free to toggle.** Because activation flips a runtime flag rather than the compiled kernel, switching a field on or off mid-simulation costs nothing and needs no rebuild.

## See also

- {doc}`emitters` for spawning streams of particles that a force field can then push around.
- {doc}`beyond_rigid_bodies` for an overview of the particle-based solvers force fields act on.
- {doc}`Force field API </api_reference/scene/force_field>` for the full parameter reference.
