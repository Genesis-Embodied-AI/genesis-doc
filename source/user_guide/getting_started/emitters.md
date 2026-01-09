# 💧 Particle Emitters

Emitters generate particles for fluid and material simulations (SPH, MPM, PBD).

## Creating an Emitter

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=4e-3, substeps=10),
    sph_options=gs.options.SPHOptions(particle_size=0.02),
)

scene.add_entity(gs.morphs.Plane())

emitter = scene.add_emitter(
    material=gs.materials.SPH.Liquid(),
    max_particles=100000,
    surface=gs.surfaces.Glass(color=(0.7, 0.85, 1.0, 0.7)),
)

scene.build()
```

## Supported Materials

- `gs.materials.SPH.Liquid()` - SPH fluid
- `gs.materials.MPM.Liquid()` - MPM liquid
- `gs.materials.MPM.Sand()` - Granular material
- `gs.materials.PBD.Liquid()` - Position-based fluid

## Directional Emission

```python
for step in range(500):
    emitter.emit(
        pos=np.array([0.5, 0.5, 2.0]),      # Nozzle position
        direction=np.array([0.0, 0.0, -1.0]), # Emission direction
        speed=5.0,                            # Particle speed
        droplet_shape="circle",               # Shape: circle, sphere, square, rectangle
        droplet_size=0.1,                     # Radius or side length
    )
    scene.step()
```

### Droplet Shapes

| Shape | `droplet_size` | Description |
|-------|---------------|-------------|
| `"circle"` | `float` | Cylindrical stream |
| `"sphere"` | `float` | Spherical droplet |
| `"square"` | `float` | Cubic droplet |
| `"rectangle"` | `(w, h)` | Rectangular stream |

## Omnidirectional Emission

Emit particles radially from a spherical source:

```python
emitter.emit_omni(
    pos=(0.5, 0.5, 1.0),
    source_radius=0.1,
    speed=2.0,
)
```

## Dynamic Emission

```python
for i in range(1000):
    # Oscillating direction
    direction = np.array([0.0, np.sin(i / 10) * 0.3, -1.0])

    emitter.emit(
        pos=np.array([0.5, 0.0, 2.0]),
        direction=direction,
        speed=8.0,
        droplet_shape="rectangle",
        droplet_size=[0.03, 0.05],
    )
    scene.step()
```

## Multiple Emitters

```python
emitter1 = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.9, 0.4, 1.0)),
)
emitter2 = scene.add_emitter(
    material=gs.materials.MPM.Liquid(),
    max_particles=500000,
    surface=gs.surfaces.Rough(color=(0.0, 0.4, 0.9, 1.0)),
)

for step in range(500):
    emitter1.emit(pos=np.array([0.3, 0.5, 2.0]), direction=np.array([0, 0, -1]), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    emitter2.emit(pos=np.array([0.7, 0.5, 2.0]), direction=np.array([0, 0, -1]), speed=3.0, droplet_shape="circle", droplet_size=0.1)
    scene.step()
```

## Notes

- Emitters must be added before `scene.build()`
- Particles recycle when `max_particles` is reached
- Not compatible with differentiable simulation (`requires_grad=True`)
