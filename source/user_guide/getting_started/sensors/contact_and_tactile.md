# Contact and tactile sensors

Contact and tactile sensors all measure how a rigid link interacts with the rest of the scene. They differ in how rich the answer is: from a single boolean ("am I touching something?"), through a net force vector, to a dense field of per-taxel forces or elastomer displacements that imitate a tactile skin. This page covers the whole family and helps you pick one.

Two mechanisms produce these readings, and the distinction matters:

- **Solver-based** sensors read contact impulses directly out of the rigid solver. `Contact`, `ContactForce`, and `JointTorque` fall here. They are physically consistent with the simulation but only exist where the solver actually resolves a contact.
- **Geometry-based** tactile probes query signed-distance fields (SDFs) or sampled point clouds around user-placed probe positions, and estimate a force from penetration and relative motion. They give you a dense taxel grid at arbitrary locations without adding contacts to the solver, at the cost of being an approximation rather than a true impulse.

Every sensor below is exercised by a runnable script under `examples/sensors/`; each section links its source of truth. For how sensors are sampled, read back, batched with `scene.read_sensors()`, and configured with noise, delay, and `history_length`, see the {doc}`sensors overview <index>`.

## Choosing a sensor

| Sensor | `read()` returns | Shape | Frame / units |
|---|---|---|---|
| `Contact` | in-contact flag | `([n_envs,] 1)` | bool |
| `ContactForce` | net contact force on the link | `([n_envs,] 3)` | link-local, N |
| `JointTorque` | actuator effort per dof | `([n_envs,] n_dofs)` | N·m (revolute) / N (prismatic) |
| `ContactProbe` | in-contact flag per probe | `([n_envs,] n_probes)` | bool |
| `ContactDepthProbe` | penetration depth per probe | `([n_envs,] n_probes)` | m |
| `KinematicTaxel` | `(force, torque)` per probe | each `([n_envs,] n_probes, 3)` | link frame, N / N·m |
| `ElastomerTaxel` | marker displacement per probe | `([n_envs,] n_probes, 3)` | link frame, m |
| `ProximityTaxel` | `(force, torque)` per probe | each `([n_envs,] n_probes, 3)` | link-local, N / N·m |

The `[n_envs,]` axis is present only when the scene is built with multiple environments. When a sensor is created with `history_length > 0`, an extra axis is inserted after the batch axis (see the {doc}`overview <index>`).

## Contact and contact force

`Contact` and `ContactForce` both read the rigid solver's contact impulses for one link. `Contact` reports whether the link is touching anything; `ContactForce` reports the net force vector acting on it, rotated into the link's own frame.

The full script is [`examples/sensors/contact_force_go2.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/contact_force_go2.py), which mounts a sensor on each foot of a Go2 quadruped (pass `--no-force` to swap `ContactForce` for `Contact`):

```python
foot_link_names = ("FR_foot", "FL_foot", "RR_foot", "RL_foot")
go2 = scene.add_entity(
    gs.morphs.URDF(
        file="urdf/go2/urdf/go2.urdf",
        pos=(0.0, 0.0, 0.2),
        links_to_keep=foot_link_names,
    )
)

for link_name in foot_link_names:
    sensor = scene.add_sensor(
        gs.sensors.ContactForce(
            entity_idx=go2.idx,
            link_idx_local=go2.get_link(link_name).idx_local,
            draw_debug=True,
        )
    )
```

A sensor is bound to one link by `entity_idx` and the entity-local `link_idx_local`. After building and stepping, read it:

```python
force = sensor.read()  # shape ([n_envs,] 3), N, in the link-local frame
```

Configuration:

- `Contact` accepts `threshold` (a positive force magnitude registers as contact above this value; default `0.0`) and `filter_link_idx`, a list of **global** link indices whose contacts with the sensor link are ignored.
- `ContactForce` clamps each axis to `[min_force, max_force]`; readings below `min_force` are zeroed and readings above `max_force` are saturated. Both default to no clamping.

```{figure} ../../../_static/images/contact_force_sensor.png
:alt: A Go2 quadruped standing on a ground plane, with a magenta arrow drawn at each foot showing the contact force reported by that foot's ContactForce sensor
```

## Joint torque

`JointTorque` measures the generalized effort delivered at each actuator's output shaft — torque for revolute dofs, force for prismatic dofs. It is a proprioceptive way to sense interaction: an external contact shows up as a change in the effort the joints must supply, without any dedicated contact sensor on the touching link.

The reading models the effort at the gearbox interface:

```
actuator_force = tau_control - armature * qacc + tau_frictionloss + tau_damping
```

Because `qacc` is the constraint-solved acceleration, gravity, Coriolis, and contact loads are all captured implicitly. In free space the reading is roughly the gravity-plus-Coriolis load; when the arm presses into an obstacle it also carries the contact reaction.

The full script is [`examples/sensors/joint_torque_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/joint_torque_franka.py), which holds a Franka arm against a fixed wall box and plots control torque against sensed torque:

```python
joint_torque = scene.add_sensor(
    gs.sensors.JointTorque(
        entity_idx=franka.idx,
        dofs_idx_local=(0, 1, 2, 3, 4, 5, 6),  # None (default) selects all dofs
    )
)

# ... build, then each step ...
tau = joint_torque.read()  # shape ([n_envs,] n_dofs)
```

## Tactile probes

Tactile probes turn a link's surface into a grid of sensing points, or **taxels**. You describe the layout once with `probe_local_pos` — a set of `(x, y, z)` offsets in the link-local frame — and the probes move rigidly with the link. Because the layout is link-local, a regular grid imitates a taxel array on a fingertip or a sensor pad.

Genesis World provides a helper for laying out a planar grid, `genesis.utils.geom.generate_grid_points_on_plane(lo, hi, normal, nx, ny)`, which returns an `(ny, nx, 3)` array of positions. Probe layout and reading follow the same shape either way: `n_probes` is the flattened probe count.

Two families share this interface but estimate contact differently:

- **SDF-query probes** — `ContactProbe`, `ContactDepthProbe`, and `KinematicTaxel` — query the signed distance from each probe to nearby collision geometry directly. They need no list of target links.
- **Point-cloud probes** — `ElastomerTaxel` and `ProximityTaxel` — sample a point cloud from the meshes named in `track_link_idx` (global link indices) and measure against those points. `n_sample_points` sets the sample budget.

Both interactive demos below let you select the sensor type with `--sensor {depth,kinematic,elastomer,proximity}`. Readings are geometric estimates, not solver impulses, and are uncalibrated — treat them as relative signals unless you tune the coefficients to your setup.

- [`examples/sensors/tactile_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_franka.py) sensorizes both Franka fingertips and lets you teleoperate a grasp.
- [`examples/sensors/tactile_sandbox.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_sandbox.py) presses controllable objects into a fixed taxel pad (box or dome), across four parallel environments.

### Contact depth and contact probes

The simplest probes report geometry alone. `ContactDepthProbe` returns the penetration depth at each probe in meters; `ContactProbe` thresholds that depth into a per-probe boolean (`contact_threshold`, default `1e-4` m).

```python
depth_probe = scene.add_sensor(
    gs.sensors.ContactDepthProbe(
        entity_idx=franka.idx,
        link_idx_local=franka.get_link("left_finger").idx_local,
        probe_local_pos=probe_local_pos.reshape(-1, 3),
        probe_radius=0.002,
    )
)

depth = depth_probe.read()  # shape ([n_envs,] n_probes), m
```

### Kinematic taxels

`KinematicTaxel` adds a spring-damper force model on top of the depth query. For each taxel it estimates a force from penetration along the probe normal and a torque from the twist, using the probe's motion relative to the object it touches:

```
s = penetration ** normal_exponent
F = -normal_stiffness * s * n  -  normal_damping * s * v_n  -  shear_scalar * v_t
```

where `n` is the probe normal, `v_n` / `v_t` are the normal and tangential relative velocities. Use `normal_exponent=1.5` for Hertzian (spherical) contact; the default `1.0` is a linear spring.

```python
taxel = scene.add_sensor(
    gs.sensors.KinematicTaxel(
        entity_idx=franka.idx,
        link_idx_local=franka.get_link("left_finger").idx_local,
        probe_local_pos=probe_local_pos.reshape(-1, 3),
        probe_local_normal=(0.0, -1.0, 0.0),  # link-local unit normal
        probe_radius=0.002,
        normal_stiffness=5000.0,
        normal_exponent=1.5,
    )
)

data = taxel.read()
data.force   # shape ([n_envs,] n_probes, 3), N, link frame
data.torque  # shape ([n_envs,] n_probes, 3), N·m, link frame
```

`read()` returns a `KinematicTaxelReturnType` named tuple, so `data.force` and `data.torque` unpack by name.

<video preload="auto" controls="True" width="100%" aria-label="A live vector-field plot of KinematicTaxel forces across a probe grid as an object presses into the sensor, with arrows growing where penetration is deepest">
<source src="../../../_static/videos/kin_probe_data.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Elastomer taxels

`ElastomerTaxel` models a soft tactile skin without simulating deformation. Each probe reports a 3D marker displacement caused by local indentation and shear against the tracked geometry, computed with a HydroShear-style model. It is the right choice when you want the visual "dot displacement" signal of a vision-based tactile sensor.

```python
tactile = scene.add_sensor(
    gs.sensors.ElastomerTaxel(
        entity_idx=franka.idx,
        link_idx_local=franka.get_link("left_finger").idx_local,
        probe_local_pos=probe_local_pos,  # (ny, nx, 3) grid, or (N, 3)
        probe_local_normal=(0.0, -1.0, 0.0),
        probe_radius=0.002,
        track_link_idx=(cube.base_link_idx,),  # global link idx to sense against
        dilate_scale=10.0,   # gain on normal indentation
        shear_scale=100.0,   # gain on tangential slip
    )
)

displacement = tactile.read()  # shape ([n_envs,] n_probes, 3), m
```

`dilate_scale` and `shear_scale` scale the indentation and shear response; `lambda_d` and `lambda_s` control how far each effect spreads across neighboring markers. When `probe_local_pos` is a regular planar grid with a single shared normal, the dilation term is computed with an FFT to keep large arrays fast.

<video preload="auto" controls="True" width="100%" aria-label="A Franka gripper with taxel grids on both fingertips grasping objects; marker displacement vectors on each fingertip deflect as the fingers make contact">
<source src="../../../_static/videos/tactile_fingertips.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

### Proximity taxels

`ProximityTaxel` estimates per-taxel force and torque from a point cloud sampled on the tracked meshes, within a spherical sensing volume of radius `probe_radius` around each taxel. It reads before hard contact, so it captures near-touch as well as touch.

```python
proximity = scene.add_sensor(
    gs.sensors.ProximityTaxel(
        entity_idx=pad.idx,
        link_idx_local=0,
        probe_local_pos=probe_local_pos.reshape(-1, 3),
        probe_local_normal=(0.0, 0.0, 1.0),
        probe_radius=0.008,
        track_link_idx=(obj.base_link_idx,),
        n_sample_points=4000,
        stiffness=200.0,
        shear_coupling=100.0,  # 0.0 disables shear, leaving only the normal channel
    )
)

data = proximity.read()
data.force   # shape ([n_envs,] n_probes, 3), N, link-local
data.torque  # shape ([n_envs,] n_probes, 3), N·m, link-local
```

Like `KinematicTaxel`, it returns a named tuple (`ProximityTaxelReturnType`) with `force` and `torque` fields.

The sandbox demo presses different objects into a taxel pad across four parallel environments:

<video preload="auto" controls="True" width="100%" aria-label="The tactile sandbox demo pressing objects into an elastomer taxel pad across four parallel environments, with marker displacement fields responding to each object's shape">
<source src="../../../_static/videos/elastomer_sandbox.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## See also

- {doc}`Sensors overview <index>` — sampling rate, `read_ground_truth()`, batched `scene.read_sensors()`, noise, delay, and `history_length`.
- {doc}`Proximity <proximity>` — nearest-distance probes to tracked mesh surfaces, without a force estimate.
- {doc}`Extending Genesis World → Sensors </user_guide/advanced_topics/sensors/index>` — the sensor pipeline and how to add your own sensor type.
