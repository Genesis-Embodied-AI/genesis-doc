# Tactile sensors

Tactile sensors turn a link's surface into a grid of sensing points, or **taxels**, and read contact geometry directly from the scene's signed-distance fields (SDFs) or sampled point clouds rather than from solver contact impulses. They give you a dense taxel field at arbitrary locations without adding contacts to the solver, at the cost of being an approximation. Because the layout is link-local, a regular grid imitates a taxel array on a fingertip or a sensor pad.

You describe the layout once with `probe_local_pos`, a set of `(x, y, z)` offsets in the link-local frame (an `(N, 3)` set or an `(M, N, 3)` planar grid), and the probes move rigidly with the link. Genesis World provides a helper for a planar grid, `genesis.utils.geom.generate_grid_points_on_plane(lo, hi, normal, nx, ny)`, which returns an `(ny, nx, 3)` array; `n_probes` is the flattened probe count.

Two families share this interface but estimate contact differently:

- **SDF-query probes** (`ContactProbe`, `ContactDepthProbe`, and `KinematicTaxel`) query the signed distance from each probe to nearby collision geometry directly. They need no list of target links.
- **Point-cloud probes** (`ElastomerTaxel` and `ProximityTaxel`) sample a point cloud from the meshes named in `track_link_idx` (global link indices) and measure against those points. `n_sample_points` sets the sample budget.

Readings are geometric estimates, not solver impulses, and are uncalibrated. Treat them as relative signals unless you tune the coefficients to your setup. The taxels also expose hardware-style [imperfections](#sensor-imperfections) for sim-to-real robustness. For how sensors are sampled, read back, and batched, see the {doc}`sensors overview <index>`.

:::{note}
**Source and citation.** These tactile sensors were introduced in [Tactile Genesis: Exploring Tactile Sensors at Scale for Learning Dexterous Tasks](https://neuroagents-lab.github.io/tactile-genesis/) (CoRL 2026). If you use them in your research, please cite:

```bibtex
@inproceedings{chung2026tactilegenesis,
  title     = {Tactile Genesis: Exploring Tactile Sensors at Scale for Learning Dexterous Tasks},
  author    = {Chung, Trinity and Yamazaki, Kashu and Patel, Dhruv and Duburcq, Alexis and Qiao, Yiling and Fragkiadaki, Katerina and Nayebi, Aran},
  booktitle = {Conference on Robot Learning (CoRL)},
  year      = {2026}
}
```

The implementation in Genesis World has since been improved and refined, so its behavior may differ from what the original paper reports.
:::

## Choosing a sensor

| Sensor | `read()` returns | Shape | Frame / units |
|---|---|---|---|
| `ContactProbe` | in-contact flag per probe | `([n_envs,] n_probes)` | bool |
| `ContactDepthProbe` | penetration depth per probe | `([n_envs,] n_probes)` | m |
| `KinematicTaxel` | `(force, torque)` per probe | each `([n_envs,] n_probes, 3)` | link frame, N / N·m |
| `ElastomerTaxel` | marker displacement per probe | `([n_envs,] n_probes, 3)` | link frame, m |
| `ProximityTaxel` | `(force, torque)` per probe | each `([n_envs,] n_probes, 3)` | link-local, N / N·m |

Two interactive demos drive these sensors:

- [`examples/sensors/tactile_franka.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_franka.py) sensorizes both Franka fingertips and lets you teleoperate a grasp (`--sensor {depth,kinematic,elastomer,proximity}`).
- [`examples/sensors/tactile_sandbox.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/tactile_sandbox.py) presses controllable objects into a fixed taxel pad (box or dome) across four parallel environments (`--sensor {contact,depth,kinematic,elastomer,proximity}`), selecting the depth backend with `--contact-depth-query {sdf,raycast}` and enabling the [imperfections](#sensor-imperfections) below with `--noise`.

## Contact depth and contact probes

The simplest probes report geometry alone. `ContactDepthProbe` returns the penetration depth at each probe in meters; `ContactProbe` thresholds that depth into a per-probe boolean.

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

`probe_radius` is the taxel's sensing radius, not a tolerance: each reading is `depth = max(0, probe_radius - signed_distance_to_surface)`, so a larger radius both extends the detection range and adds a constant offset to the reported depth. The SDF-query probes select the contact-depth backend with `contact_depth_query`: `"sdf"` (default) queries each geom's analytic SDF grid, while `"raycast"` walks the rigid solver's collision-mesh BVH and takes the signed distance to the nearest triangle (sharing the BVH with `RaycasterSensor`). The mode is class-wide: all sensors of the same class must agree.

`ContactProbe` gates its boolean output with a Schmitt trigger to suppress chatter: it latches on when depth reaches `contact_threshold` (default `1e-4` m) and releases when depth falls back to `release_threshold` (default equals `contact_threshold`, i.e. no hysteresis; may be negative to require separation before release).

<video preload="auto" controls="True" width="100%" aria-label="A live plot of ContactDepthProbe readings across a taxel pad as an object presses in, each taxel's depth rising with local penetration">
<source src="../../_static/videos/contact_depth_probe.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## Kinematic taxels

`KinematicTaxel` adds a spring-damper force model on top of the depth query. For each taxel it estimates a force from penetration along the contact surface normal and a torque from the twist, using the probe's motion relative to the object it touches:

```
s = penetration ** normal_exponent
F = normal_stiffness * s * n  +  normal_damping * s * v_n  -  shear_scalar * v_t
```

where `n` is the contact surface normal at the probe: the SDF gradient in `"sdf"` mode, or the nearest-triangle face normal in `"raycast"` mode (see `contact_depth_query` above). `v_n` / `v_t` are the normal and tangential relative velocities. Unlike the point-cloud taxels below, `KinematicTaxel` derives `n` from the queried geometry itself rather than from a user-supplied `probe_local_normal`. Use `normal_exponent=1.5` for Hertzian (spherical) contact; the default `1.0` is a linear spring.

```python
taxel = scene.add_sensor(
    gs.sensors.KinematicTaxel(
        entity_idx=franka.idx,
        link_idx_local=franka.get_link("left_finger").idx_local,
        probe_local_pos=probe_local_pos.reshape(-1, 3),
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

<video preload="auto" controls="True" width="100%" aria-label="A live vector-field plot of KinematicTaxel forces across a probe grid as an object presses into the sensor, with arrows growing where penetration is deepest and curved twist arrows tracking rotational slip">
<source src="../../_static/videos/kinematic_taxel.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## Elastomer taxels

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

`dilate_scale` and `shear_scale` scale the indentation and shear response; `lambda_d` and `lambda_s` control how far each effect spreads across neighboring markers. The out-of-plane (normal) bulge scales as `depth ** normal_exponent` (default `2.0`, the HydroShear quadratic response); tangential dilation and shear stay linear in depth regardless of `normal_exponent`. When `probe_local_pos` is a regular planar grid with a single shared normal, the dilation term is computed with an FFT to keep large arrays fast. The shear anchor is gated by the same `contact_threshold` / `release_threshold` Schmitt trigger (a tracked point begins anchoring shear at `contact_threshold` penetration and releases once it separates back to `release_threshold`).

<video preload="auto" controls="True" width="100%" aria-label="A live vector-field plot of ElastomerTaxel marker displacements across a taxel pad as an object presses and slides, the dots deflecting under local indentation and shear">
<source src="../../_static/videos/elastomer_taxel.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## Proximity taxels

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

<video preload="auto" controls="True" width="100%" aria-label="A live vector-field plot of ProximityTaxel force and twist across a taxel pad as an object approaches and presses in, the field responding before and through contact">
<source src="../../_static/videos/proximity_taxel.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## Sensor imperfections

On top of the generic per-sensor imperfections (`noise`, `bias`, `resolution`, `delay`, `jitter`, available on every sensor), the tactile probe and taxel sensors expose hardware-style imperfections. They apply to the **measured branch only**: `read()` returns the imperfect signal, while `read_ground_truth()` stays clean.

| Option(s) | Models | Applies to |
|---|---|---|
| `hysteresis_strength`, `hysteresis_tau` | Viscoelastic (single-Maxwell) hysteresis: a step input overshoots by `hysteresis_strength` and relaxes with time constant `hysteresis_tau` seconds; cyclic input traces a loading-unloading loop (equilibrium gain 1). | All probes and taxels |
| `probe_gain`, `probe_gain_resample_range` | Per-taxel multiplicative gain on the measured contact depth (scalar or per-taxel array); with a range, resampled uniformly on each `scene.reset()`. | All probes and taxels |
| `dead_taxel_probability`, `dead_taxel_value_range` | Per-taxel Bernoulli chance of going dead on each `scene.reset()`; a dead taxel's output is replaced by a constant drawn from `dead_taxel_value_range`. | All probes and taxels |
| `crosstalk_strength`, `crosstalk_sigma` | Gaussian spatial crosstalk: each taxel's force/torque bleeds onto its grid neighbors (`crosstalk_strength=1` is a pure Gaussian blur of width `crosstalk_sigma`). | Grid taxels: `KinematicTaxel`, `ProximityTaxel` |
| `crosstalk_kernel` | Explicit point-spread kernel for spatial crosstalk (odd dims; center tap is the self weight). Mutually exclusive with the Gaussian options. `genesis.utils.misc.gaussian_crosstalk_kernel(n_rows, n_cols, sigma)` builds an L1-normalized Gaussian kernel. | Grid taxels: `KinematicTaxel`, `ProximityTaxel` |

Spatial crosstalk requires a regular planar `(M, N, 3)` grid `probe_local_pos`; pad irregular layouts with `probe_radius=0` filler taxels, which read zero and are skipped.

```python
import genesis.utils.misc as misc

taxel = scene.add_sensor(
    gs.sensors.KinematicTaxel(
        entity_idx=platform.idx,
        link_idx_local=0,
        probe_local_pos=grid_positions,  # (M, N, 3) grid
        probe_radius=0.004,
        # measured-branch imperfections:
        hysteresis_strength=0.5,
        hysteresis_tau=0.1,
        probe_gain=1.5,
        crosstalk_kernel=misc.gaussian_crosstalk_kernel(3, 3, sigma=1.0),
    )
)
```

Pass `--noise` to `tactile_sandbox.py` to enable these imperfections in the interactive demo.

<video preload="auto" controls="True" width="100%" aria-label="A live vector-field plot of KinematicTaxel forces with imperfections enabled, the field lagging and blurring across neighboring taxels from hysteresis and spatial crosstalk as an object presses in">
<source src="../../_static/videos/imperfect_kinematic_taxel.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>

## See also

- {doc}`Contact <contact>`: solver-based link-level contact, contact force, and joint torque.
- {doc}`Sensors overview <index>`: sampling rate, `read_ground_truth()`, batched `scene.read_sensors()`, noise, delay, and `history_length`.
- {doc}`Extending Genesis World → Sensors </user_guide/sensing/custom_sensors/index>`: the sensor pipeline and how to add your own sensor type.
