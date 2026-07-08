# Drone entity

A `DroneEntity` is a quadrotor whose actuation is its four propeller speeds. Unlike a robot arm, you do not command joint torques or positions; you set each propeller's angular velocity in **RPM** (revolutions per minute), and Genesis World converts those speeds into the aerodynamic forces that lift and steer the drone.

This page explains that RPM-to-motion mapping and how to drive it. It uses the Crazyflie 2.X model that ships with Genesis World. For the class API, see the {doc}`DroneEntity reference </api_reference/entity/drone_entity>`.

## How propeller RPM becomes motion

Each simulation step, Genesis World reads the RPM you set for every propeller and applies two things to that propeller's link:

- **Thrust**, a force along the propeller's local +Z axis: `F = KF · rpm²`.
- **Reaction torque**, a yaw moment about the same axis: `τ = KM · rpm² · spin`, where `spin` is `+1` for a counter-clockwise propeller and `-1` for a clockwise one.

`KF` (thrust coefficient) and `KM` (moment coefficient) are read from the drone's URDF, so they are fixed properties of the model. Thrust grows with the *square* of RPM, so control is nonlinear: doubling RPM roughly quadruples lift.

Two consequences follow, and they are the whole basis of quadrotor control:

- **Common RPM sets altitude.** Spinning all four propellers equally produces pure vertical thrust. There is a hover RPM at which total thrust balances gravity.
- **Differential RPM sets attitude.** Speeding up one side relative to the other tilts the drone (roll/pitch), which redirects the thrust vector and produces horizontal motion. Speeding up the counter-clockwise pair relative to the clockwise pair leaves a net yaw torque, which rotates the drone in place.

:::{note}
Drone entities do not support collision checking. They interact with the world only through the propeller forces described above and through gravity.
:::

## Minimal example: hover

The complete runnable script for programmed flight is [`examples/drone/fly.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/fly.py). The following is the smallest program that keeps a drone aloft: create it, then set every propeller to the hover RPM on each step.

```python
import genesis as gs

gs.init(backend=gs.cpu)

scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),  # gravity defaults to (0, 0, -9.81) m/s²
)
scene.add_entity(gs.morphs.Plane())
drone = scene.add_entity(
    gs.morphs.Drone(file="urdf/drones/cf2x.urdf", pos=(0.0, 0.0, 0.5)),
)

scene.build()

hover_rpm = 14468.429  # balances gravity for the CF2X model
for _ in range(1000):
    drone.set_propellers_rpm([hover_rpm, hover_rpm, hover_rpm, hover_rpm])
    scene.step()
```

The hover RPM is model-specific; it is the value at which `4 · KF · rpm²` equals the drone's weight. For the shipped Crazyflie 2.X it is approximately 14468 RPM.

## The drone morph

The morph is a URDF loaded through `gs.morphs.Drone`. The defaults match the Crazyflie model, so `file` and `pos` are usually all you need:

```python
drone = scene.add_entity(
    gs.morphs.Drone(
        file="urdf/drones/cf2x.urdf",
        model="CF2X",  # "CF2X", "CF2P", or "RACE"
        pos=(0.0, 0.0, 0.5),  # meters, Z-up
        euler=(0.0, 0.0, 0.0),  # scipy extrinsic x-y-z, degrees
        propellers_link_name=("prop0_link", "prop1_link", "prop2_link", "prop3_link"),
        propellers_spin=(-1, 1, -1, 1),  # per propeller: -1 = CW, +1 = CCW
    ),
)
```

`propellers_link_name` fixes the *order* in which propellers are indexed: the RPM array you pass to `set_propellers_rpm` maps to these links positionally. `propellers_spin` gives each propeller's rotation direction, which sets the sign of its yaw reaction torque. The `RACE` model inverts all four spins internally.

The bundled models are:

| `model` | `file` | Description |
|---|---|---|
| `CF2X` | `urdf/drones/cf2x.urdf` | Crazyflie 2.X, X rotor layout |
| `CF2P` | `urdf/drones/cf2p.urdf` | Crazyflie 2.X, plus rotor layout |
| `RACE` | `urdf/drones/racer.urdf` | Racing quadrotor |

## Setting propeller RPM

`set_propellers_rpm` is the single actuation call. It takes one RPM per propeller:

```python
propellers_rpm  # shape ([n_envs,] n_propellers), non-negative
```

:::{warning}
Call `set_propellers_rpm` **exactly once per step**, before `scene.step()`. A second call in the same step raises an error, because the propeller revolution count used for the spin animation is accumulated per step.
:::

To move rather than hover, offset individual propellers from the hover RPM. The interactive example [`examples/drone/interactive_drone.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/interactive_drone.py) maps a direction to a per-propeller offset around a common thrust:

```python
# cur_dir is a 4-vector of per-propeller deltas in [-1, 1]
clipped_dir = np.clip(self.cur_dir, -1.0, 1.0)
rpms = self.thrust + clipped_dir * self.rotation_delta
return np.clip(rpms, 0, 25000)  # keep RPM within the motor's range
```

The direction vectors show the pattern directly: moving forward uses `(1, 1, -1, -1)` (front pair up, rear pair down, so the drone pitches forward), while yaw-style rotation uses `(-1, 1, -1, 1)`, matching the propeller spin directions.

## Closed-loop control

Open-loop RPM schedules drift. To fly to a target position, close the loop on the drone's state. The state getters are inherited from `RigidEntity`:

```python
pos = drone.get_pos()  # shape ([n_envs,] 3), meters
vel = drone.get_vel()  # shape ([n_envs,] 3), m/s
quat = drone.get_quat()  # shape ([n_envs,] 4), (w, x, y, z)
```

[`examples/drone/quadcopter_controller.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/quadcopter_controller.py) implements a cascaded PID controller (position → velocity → attitude) whose final stage is a **mixer** that turns desired thrust, roll, pitch, and yaw corrections into four motor RPMs:

```python
M1 = self.__base_rpm + (thrust - roll - pitch - yaw - x_vel + y_vel)
M2 = self.__base_rpm + (thrust - roll + pitch + yaw + x_vel + y_vel)
M3 = self.__base_rpm + (thrust + roll + pitch - yaw + x_vel - y_vel)
M4 = self.__base_rpm + (thrust + roll - pitch + yaw - x_vel - y_vel)
```

Each correction adds or subtracts across the four motors according to its sign pattern, which is exactly the differential-RPM idea made concrete. Run the full point-to-point flight with [`examples/drone/fly_route.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/drone/fly_route.py), which drives this controller and clamps each RPM to a safe range before applying it.

## Multiple environments

RPM control batches across {doc}`parallel environments <parallel_simulation>`. Build with `n_envs`, then pass one RPM row per environment:

```python
scene.build(n_envs=32)

# shape (n_envs, n_propellers)
rpms = np.tile([hover_rpm] * drone.n_propellers, (32, 1))
drone.set_propellers_rpm(rpms)
```

## See also

- {doc}`Training a drone to hover <policy_training/examples/hover_env>` — a complete reinforcement-learning environment built on this entity.
- {doc}`Training locomotion policies <policy_training/examples/locomotion>` — the same training workflow applied to legged robots.
- {doc}`DroneEntity reference </api_reference/entity/drone_entity>` — the full class API.
