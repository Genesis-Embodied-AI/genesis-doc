# 🚁 Drone Entity

Genesis provides specialized drone simulation with propeller physics and motor control.

## Creating a Drone

```python
import genesis as gs
import numpy as np

gs.init(backend=gs.gpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01, gravity=(0, 0, -9.81)),
)

scene.add_entity(gs.morphs.Plane())

drone = scene.add_entity(
    morph=gs.morphs.Drone(
        file="urdf/drones/cf2x.urdf",
        model="CF2X",
        pos=(0.0, 0.0, 0.5),
    ),
)

scene.build()
```

## Drone Morph Options

```python
gs.morphs.Drone(
    file="urdf/drones/cf2x.urdf",  # URDF file path
    model="CF2X",                   # Model: "CF2X", "CF2P", or "RACE"
    pos=(0.0, 0.0, 0.5),           # Initial position
    euler=(0.0, 0.0, 0.0),         # Initial orientation (degrees)
    propellers_link_name=('prop0_link', 'prop1_link', 'prop2_link', 'prop3_link'),
    propellers_spin=(-1, 1, -1, 1), # Spin directions: 1=CCW, -1=CW
)
```

## Motor Control

Control propellers via RPM (revolutions per minute):

```python
hover_rpm = 14475.8  # Approximate hover RPM for CF2X
max_rpm = 25000.0

for step in range(1000):
    # Set RPM for each propeller [front-left, front-right, back-left, back-right]
    rpms = np.array([hover_rpm, hover_rpm, hover_rpm, hover_rpm])

    # Add differential thrust for motion
    rpms[0] += 100  # Increase front-left
    rpms[3] += 100  # Increase back-right
    rpms = np.clip(rpms, 0, max_rpm)

    drone.set_propellels_rpm(rpms)  # Call ONCE per step
    scene.step()
```

**Important:** `set_propellels_rpm()` must be called exactly once per simulation step.

## Physics Model

- **Thrust:** `F = KF × RPM²` (vertical force per propeller)
- **Torque:** `τ = KM × RPM² × spin_direction` (yaw moment)
- **Control:**
  - Differential thrust between propellers → translation
  - Differential moment between pairs → rotation

## Multi-Environment

```python
scene.build(n_envs=32)

# Control shape: (n_envs, n_propellers)
rpms = np.tile([hover_rpm] * 4, (32, 1))
drone.set_propellels_rpm(rpms)
```

## Available Models

| Model | File | Description |
|-------|------|-------------|
| CF2X | `urdf/drones/cf2x.urdf` | Crazyflie 2.0 X-config |
| CF2P | `urdf/drones/cf2p.urdf` | Crazyflie 2.0 Plus |
| RACE | `urdf/drones/racer.urdf` | Racing drone |

## Example: Hover Control

```python
import genesis as gs
import numpy as np

gs.init()
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
drone = scene.add_entity(gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0, 0, 1)))
scene.build()

target_height = 1.0
kp = 5000.0

for _ in range(500):
    pos = drone.get_pos()[0]
    error = target_height - pos[2].item()

    base_rpm = 14475.8
    correction = kp * error
    rpms = np.clip([base_rpm + correction] * 4, 0, 25000)

    drone.set_propellels_rpm(rpms)
    scene.step()
```
