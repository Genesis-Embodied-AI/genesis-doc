# Particle emitters

An emitter is a nozzle that streams particles into a particle solver as the simulation runs. Where {doc}`Beyond rigid bodies <beyond_rigid_bodies>` fills a fixed volume of particles once at build time, an emitter injects new particles every step — a faucet, a hose, or a jet of sand that keeps flowing for as long as you call it.

An emitter does not simulate anything itself. It owns a particle entity, pre-allocated with `max_particles` slots, and feeds positions and velocities into that entity's solver. The material you give the emitter decides which solver runs the particles: `gs.materials.SPH.*` for smoothed-particle hydrodynamics, `gs.materials.MPM.*` for the material point method, and `gs.materials.PBD.*` for position-based dynamics.

The complete script is [`examples/coupling/water_wheel.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/coupling/water_wheel.py):

```python
import numpy as np
import genesis as gs

gs.init()

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
    sph_options=gs.options.SPHOptions(particle_size=0.02),  # meters
)

scene.add_entity(gs.morphs.Plane())

emitter = scene.add_emitter(
    material=gs.materials.SPH.Liquid(),
    max_particles=100000,
    surface=gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7)),
)

scene.build()

for i in range(500):
    emitter.emit(
        pos=(0.5, 1.0, 3.5),          # nozzle position, meters, Z-up
        direction=(0.0, 0.0, -1.0),   # aimed straight down
        speed=5.0,                    # m/s
        droplet_shape="circle",
        droplet_size=0.22,            # stream diameter, meters
    )
    scene.step()
```

## Add the emitter

`scene.add_emitter()` must run before `scene.build()`, like any other entity. It allocates the particle entity and returns an {doc}`Emitter </api_reference/entity/emitter>` handle you call each step:

```python
emitter = scene.add_emitter(
    material=gs.materials.SPH.Liquid(),
    max_particles=100000,
    surface=gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7)),
)
```

- `material` selects the solver and the physical behavior. It must be one of `gs.materials.MPM.Base`, `gs.materials.SPH.Base`, `gs.materials.PBD.Particle`, or `gs.materials.PBD.Liquid` (or a subclass: `SPH.Liquid`, `MPM.Liquid`, `MPM.Sand`, `PBD.Liquid`). Passing an unsupported material raises at `add_emitter` time.
- `max_particles` caps how many particles the emitter holds. Once emission reaches the cap, the oldest particles are recycled, so a long-running stream stays bounded in memory. Default is `20000`.
- `surface` controls appearance only. If omitted, the emitter uses `gs.surfaces.Default(color=(0.6, 0.8, 1.0, 1.0))`. `vis_mode="visual"` is not supported for emitters; use the default `"particle"`, or `"recon"` to render a reconstructed fluid surface.

## Emit each step

Emission is per-step: one `emit()` call injects one segment of the stream, and calling it every step produces continuous flow. Stop calling it and the stream stops while the already-emitted particles keep simulating.

```python
emitter.emit(
    pos=(0.5, 1.0, 3.5),
    direction=(0.0, 0.0, -1.0),
    speed=5.0,
    droplet_shape="circle",
    droplet_size=0.22,
)
```

`pos` is the world-space nozzle position in meters (Z-up). `direction` is normalized internally, so only its orientation matters, not its length. `speed` is the emission speed in m/s and also sets each particle's initial velocity along `direction`.

When you leave `droplet_length` unset, the emitter sizes each segment from the motion in one step, `speed * dt`. If that length is shorter than one particle, the emitter accumulates it and emits nothing until enough has built up, so a slow stream still forms whole particles rather than dropping them.

## Droplet shapes

`droplet_shape` sets the cross-section of the emitted geometry; `droplet_size` sets its extent, in meters.

| `droplet_shape` | `droplet_size` | Emits |
|---|---|---|
| `"circle"` | `float` (diameter) | A cylindrical stream along `direction`. |
| `"sphere"` | `float` (diameter) | A single spherical droplet; ignores `droplet_length`. |
| `"square"` | `float` (side length) | A square-section stream along `direction`. |
| `"rectangle"` | `(width, height)` | A rectangular-section stream along `direction`. |

`theta` rotates the droplet about its emission axis, in radians. `p_size` overrides the sampling particle size (defaults to the solver's).

Steering the direction over time bends the stream. `examples/coupling/sand_wheel.py` sweeps a sand jet back and forth this way:

```python
for i in range(1000):
    emitter.emit(
        pos=(0.5, 0.0, 2.3),
        direction=(0.0, np.sin(i / 10) * 0.35, -1.0),  # oscillating aim
        speed=8.0,
        droplet_shape="rectangle",
        droplet_size=[0.03, 0.05],  # width, height in meters
    )
    scene.step()
```

## Omnidirectional emission

`emit_omni()` releases particles radially from a spherical shell instead of a directed nozzle: a burst or fountain rather than a stream. Each particle's velocity points outward from the center at `speed`:

```python
emitter.emit_omni(
    pos=(0.5, 0.5, 1.0),   # center of the source, meters
    source_radius=0.1,     # shell radius, meters
    speed=2.0,             # m/s, radially outward
)
```

## Multiple emitters

Each emitter owns its own particle entity, so add as many as you need: different materials, positions, and surfaces coexist in one scene. Call `emit()` on each within the same step loop.

```python
emitter_a = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.9, 0.4, 1.0)),
)
emitter_b = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.4, 0.9, 1.0)),
)

for i in range(500):
    emitter_a.emit(pos=(0.3, 0.5, 2.0), direction=(0, 0, -1), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    emitter_b.emit(pos=(0.7, 0.5, 2.0), direction=(0, 0, -1), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    scene.step()
```

## Notes and gotchas

:::{warning}
The emitter must fit its solver's simulation domain. If an `emit()` call would place particles outside the solver boundary, it raises rather than clipping silently. Aim the nozzle inside the bounds set by `mpm_options` / `sph_options`.
:::

:::{note}
Emitters are not available in differentiable mode. Building the scene with `requires_grad=True` and then adding an emitter raises an exception.
:::

## See also

- {doc}`Beyond rigid bodies <beyond_rigid_bodies>`: the SPH, MPM, and PBD solvers that emitted particles feed into.
- {doc}`Soft robots <soft_robots>`: muscle-actuated soft and hybrid entities built on the same particle solvers.
