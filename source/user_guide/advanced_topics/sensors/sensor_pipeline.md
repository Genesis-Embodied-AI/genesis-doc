# 🛰️ Sensor Pipeline

Genesis sensors model the **robot-control view** of a sensor - what the application code actually queries from a robot's onboard software, not what the analog hardware does at the wire level. This page explains the abstraction, the per-step pipeline that produces the user-facing measurement, and the buffering scheme that lets `read()` be a constant-time memory lookup.

For how to write your own sensor, see [Implementing Custom Sensors](custom_sensors.md).

## The abstraction: an embedded sampler writing to shared memory

A real robot does not pull values through an analog wire on each control-loop iteration. The data flow is:

```
sensor hardware ─► (analog wire, ADC, electronics noise, sensor's own bandwidth + response time)
                ─► firmware-level signal processing (filtering, calibration, conversion)
                ─► embedded firmware writes a digital snapshot into shared memory
                ─► `sensor.read()` queries shared memory and returns whatever value is currently there
```

The robot's `read()` is a **memory lookup**. It does not trigger sensor acquisition. The sensor was sampled asynchronously, possibly milliseconds ago, by an embedded process running at its own rate. Two `read()` calls in the same control-loop timestep return the **same value** because no new snapshot has been written between them. The reading is stable for the duration of one sampling period.

This shapes every design decision in the pipeline. Imperfections split into two layers depending on where the imperfection physically lives:

- **Physics-level imperfections** are properties of the physical phenomenon being sensed (e.g. genuine drift in the simulated process, low-pass coupling in a thermistor's surroundings). They accumulate through the sensor's response model and therefore must propagate through transform recurrence. They are written into the timeline ring and read by `_apply_transform` on the following step.
- **Hardware-level imperfections** are properties of the sensor's own readout stage (electronic noise, ADC quantization, sensor-output drift). They are applied at the sensor-output stage, on the per-step working buffer - never on the timeline ring. The post-`_post_process` snapshot is frozen into the return-space ring slot 0, so each captured snapshot carries the imperfection state that was sampled at that step. Transform recurrence reads only the timeline ring (clean of hardware noise), so a stateful response model (thermal dissipation, low-pass filter) is never amplified by hardware noise of the previous step.
- **Delay (and its jitter)** is the staleness of the snapshot relative to "now". A sensor with `delay = D` (plus a random `jitter` drawn each step) means: at control-loop time `t`, the robot's read returns the post-everything value captured at time `t - D - jitter_t` (response-model output + the hardware imperfection sample that was drawn at that step). `delay` and `jitter` always travel together - jitter cannot exceed delay. Sampling is zero-order-hold (ZOH) by default, which is dtype-safe for arbitrary return types (bool, uint8, quantized float) and is the right semantics for a snapshot that is meant to look "frozen at capture". Sensors whose return space is a continuous-valued float and that benefit from a smoother sampling rule can override `_apply_delay`.
- **Reads are idempotent within a step.** If a design implies they aren't, the abstraction is broken.
- **History reads** (`sensor.read(history_length=N)`) return the `N` most recent **final** measurements, i.e. snapshots of the post-everything value (post-delay, post-hardware, post-cast) at each past step.

## Class hierarchy

```
Sensor                       (minimal contract)
└── SimpleSensor             (standard pipeline; most Genesis sensors derive from this)
    ├── ContactSensor
    ├── ContactForceSensor
    ├── IMUSensor
    ├── ProximitySensor
    ├── RaycasterSensor
    ├── KinematicContactProbe
    ├── ElastomerDisplacementSensor
    └── TemperatureGridSensor

Camera (RasterizerCameraSensor, RaytracerCameraSensor, BatchRendererCameraSensor) derives from `Sensor` directly
- it has its own rendering path and does not use the SimpleSensor pipeline.
```

`Sensor` is the minimal customization contract - a single abstract per-step compute method (`_update_shared_cache`), four spec accessors (`_get_return_format` / `_get_intermediate_format` as instance methods for shape; `_get_cache_dtype` / `_get_intermediate_dtype` as classmethods for dtype), a `_post_process` projection (identity by default), and a class-level capability flag (`uses_ring_pipeline: ClassVar[bool] = True`) telling the manager whether to allocate the per-step timeline rings (GT + measured) for the class. `SimpleSensor` builds the standard pipeline on top, exposing five override hooks (`_update_raw_data`, `_update_current_timestep_data`, `_apply_physics_imperfections`, `_apply_transform`, `_apply_hardware_imperfections`) that concrete sensors override as needed. Signatures, contracts, and worked examples are in [Implementing Custom Sensors](custom_sensors.md). This page focuses on what those hooks *do* at runtime - the order in which they fire and the buffers they read and write.

## Per-step pipeline

```
[per-step, driven by SimpleSensor's orchestrator]

  _update_current_timestep_data
            │  raw -> GT intermediate cache  (kernel target, contiguous (cols, B))
            │  mirrored to GT timeline ring slot 0  +  measured timeline ring slot 0
            │
            ├──► [GT branch]
            │       │
            │       ▼
            │   _apply_transform(GT slot 0, timeline=GT timeline ring)
            │       │  (reads previous slots for stateful response models)
            │       ▼
            │   GT slot 0 is the post-transform value; copied back into GT
            │   intermediate cache
            │       │
            │       ▼
            │   _post_process(GT intermediate, timeline=GT return ring, is_measured=False)
            │       │  (cast / clamp / mask, optionally stateful via return ring)
            │       ▼
            │   write to GT return-space ring slot 0  (post-everything snapshot)
            │       │
            │       ▼
            │   read GT return ring at(0) -> per-class GT return cache (GT has no delay)
            │
            └──► [measured branch]
                    │
                    ▼
                _apply_physics_imperfections(measured slot 0)
                    │  (default no-op; physics-level imperfections that should
                    │   propagate through transform recurrence)
                    ▼
                _apply_transform(measured slot 0, timeline=measured timeline ring)
                    │  (recurrence reads clean pre-hardware previous slots)
                    ▼
                measured slot 0 holds post-physics, post-transform value
                    │
                    ▼
                copy measured ring slot 0 -> per-dtype intermediate cache
                (the per-step working buffer)
                    │
                    ▼
                _apply_hardware_imperfections(intermediate cache)
                    │  (stateless noise/bias/random_walk/resolution applied on the
                    │   per-step working buffer; never written into the timeline
                    │   ring, so transform recurrence stays clean)
                    ▼
                _post_process(intermediate cache, timeline=measured return ring, is_measured=True)
                    │  (cast / clamp / mask; stateful HW responses such as a
                    │   sensor-element bandwidth filter live here, reading
                    │   `timeline.at(0)` for the previous post-everything output -
                    │   the return ring rotates after this call returns)
                    ▼
                write to measured return-space ring slot 0  (post-everything snapshot,
                with this step's hardware noise frozen in)
                    │
                    ▼
                delay sampling: read stale slot at (delay + jitter) steps back
                from the measured return ring -> per-class measured return cache
                    │  (per-env offsets; each delayed slot carries its own frozen
                    │   imperfection state from the step at which it was captured)
                    ▼
                user-visible read value

[read paths - idempotent within a step]

  Sensor.read()                          ─► view of the measured return cache for this sensor
                                            (post-delay-sample when delay > 0; otherwise the
                                            current step's post-everything value)
  Sensor.read_ground_truth()             ─► same, ground-truth side (no delay)
  Sensor.read(history_length=N)          ─► fresh tensor with the last N snapshots,
                                            gathered from the per-class return-space ring
  SensorManager.read_sensors()           ─► fresh tensor per class; per-class return cache
                                            (no history) or per-class return-space ring (history).
```

### The intermediate-vs-return separation

The pipeline operates in **intermediate space** through every stage up to and including `_apply_hardware_imperfections` (transform, physics imperfections, hardware imperfections all read and write intermediate-space values). Casting (bool threshold, clamp, mask, deadband) lives in `_post_process`, which projects intermediate space to return space. The return-space ring stores those projected snapshots; delay sampling then reads previous slots of that ring and writes them into the per-class return cache (shape declared by `_get_return_format`, dtype by `_get_cache_dtype`).

The separation is **structural, not aesthetic**. `_apply_transform(timeline=...)` lets filter overrides read previous slots of the timeline ring (e.g. `timeline.at(1)` for the previous frame); those slots must be in the **same data space** as the `data` argument the override receives, otherwise the filter mixes apples and oranges and silently produces wrong output. So the timeline ring holds intermediate-space values; the return cache and the return-space ring are in return space.

When `_post_process` is identity AND no delay/history is configured, the manager allocates a single buffer and aliases `return_cache` as a view of the intermediate slice - no extra storage. When `_post_process` is overridden (ContactSensor: float to bool; ContactForceSensor: clamp + masked_fill), the return cache is a distinct buffer fed by the return-space ring. The author signals the intermediate / return distinction by overriding `_get_intermediate_format` and/or `_get_intermediate_dtype` (a no-op override returning the return-space value is acceptable when shape and dtype coincide).

### Why shape is per-instance and dtype is class-uniform

`_get_return_format` and `_get_intermediate_format` are instance methods. Sensor options are free to affect the returned shape - `Raycaster.pattern.return_shape`, `Camera.res`, `Proximity.probe_local_pos`, `TemperatureGrid.grid_size`, etc. This is supported by design; the manager accumulates each instance's contribution into the per-class slice when sizing buffers.

`_get_cache_dtype` and `_get_intermediate_dtype` are classmethods. Dtype is class-uniform - one dtype per sensor class, shared by every instance. This is a load-bearing invariant of the manager: the per-class slice into the per-dtype intermediate buffer must be contiguous. If two instances of the same class had different dtypes, the per-class slice would no longer be a single contiguous range in one buffer, the per-class metadata fields (`ContactSensorMetadata.thresholds`, `IMUSharedMetadata.magnetic_field_vector`, ...) would have to be split, and the once-per-step `_update_shared_cache` / `_apply_transform` contract would degenerate into multiple per-(class, dtype) sub-batches. Use two different sensor classes if you need different dtypes.

### Why `_post_process` is eager (write-time), not lazy (read-time)

Three reasons:

1. **Deterministic call count.** The manager calls `_post_process` a fixed number of times per simulation step (once per branch), independent of how many consumers (controller + logger + visualization) `read()` the sensor. A lazy (read-time) placement would re-invoke the projection N times per step for N consumers, which is wasteful and breaks any stateful override.
2. **Real per-class return storage.** Without eager projection, the per-class return cache wouldn't exist and `_post_process` overrides would have to allocate fresh tensors at every read. Eager placement means the manager owns a real per-class buffer of post-processed values that every read path (single sensor or bulk class read) gathers from.
3. **Amortized cost.** A typical control loop reads each sensor once per step from the controller, again from a logger, again from visualization. Eager projection runs the post-process once per step regardless of read fan-out. Lazy projection would re-run it per consumer.

## Storage scopes and the per-step loop

The manager owns all storage. Conceptually there are four scopes:

- **Per-dtype intermediate storage** - one buffer per data type used by sensors with that dtype, holding pipeline-internal values that hooks like `_apply_transform` and `_apply_hardware_imperfections` read and write. A contiguous slice within this buffer belongs to each sensor class.
- **Per-class return storage** - one buffer per sensor class in the return space declared by `_get_return_format` / `_get_cache_dtype`. When no per-class return-space ring is needed (identity `_post_process`, no delay, no history) the return cache is a zero-copy alias-view of the intermediate cache; otherwise it is a distinct buffer that the orchestrator fills from the return-space ring (via delay sampling on the measured side, slot-0 read on the GT side).
- **Per-dtype timeline rings** (GT + measured) - paired circular buffers in intermediate space, holding post-transform, **PRE-hardware-imperfection** snapshots. Allocated together when any sensor class in the dtype declares `uses_ring_pipeline = True` (the default). Sized `max(2, max_history)` - two slots are enough for the staging buffer + one-step recurrence used by `_apply_transform`, and growing to `max_history` when any sensor in the dtype requests history lets multi-tap stateful filters inside `_apply_transform` read deeper without keeping their own state. The two share their rotation index so a single rotation advances both.
- **Per-class return-space rings** (GT + measured) - paired circular buffers in return space (post-`_post_process`, pre-delay-sample). Allocated whenever any sensor in the class has `delay > 0` OR `history_length > 0` OR the class overrides `_post_process`. Each step the post-everything snapshot is written to slot 0; delay sampling and history reads both source from here. Sized `max(max_delay+1, max_history, 2_if_post_process_overridden)`. Each delayed slot carries its own frozen imperfection state from the step at which it was captured. GT and measured rings share their rotation index.

Per simulation step the manager:

1. Rotates the per-dtype timeline ring pair and the per-class return-space ring pair, freeing the oldest slot for the new snapshot.
2. For each sensor class, invokes `_update_shared_cache` once, passing the per-class slices of the intermediate cache, both timeline rings (GT + measured; `None` for classes that opted out), and the per-class return cache. The hook produces the ground-truth signal in the GT intermediate cache and the measured snapshot (post-physics, post-transform, post-hardware-imperfections) in the per-step working buffer.
3. Runs `_post_process` on both branches and writes the result to slot 0 of the per-class return-space ring pair. Skipped when no return-space ring is allocated (alias-view propagates the per-step write automatically).
4. Reads slot 0 of the GT return ring into the GT return cache; per-sensor delay-samples the measured return ring into the measured return cache. For sensors with `delay = 0` and no jitter this is just slot-0 reads.

`read_sensors(envs_idx=...)` always returns a fresh tensor per class, independent of internal sensor storage. Non-history reads gather the current snapshot from the per-class return cache; history reads gather the last `N` snapshots from the appropriate return-space ring. The caller is free to mutate the result.

## Options and their pipeline semantics

Two options classes feed the pipeline. `SensorOptions` carries the time-related knobs that every sensor exposes; `SimpleSensorOptions(SensorOptions)` adds the imperfection parameters that the SimpleSensor branch interprets. Camera, deriving from `Sensor` directly, only sees the time-related fields. The semantic of every parameter is its effect inside the pipeline diagram above:

| Option | Default | Where it acts |
|---|---|---|
| `delay` | 0.0 | Read offset into the measured return-space ring (seconds, snapshot age). A delayed read returns the post-everything value that was produced D steps ago, with the imperfections frozen at that step. |
| `jitter` | 0.0 | Random additive delay per env, sampled `Uniform[0, jitter)` each step. Must be <= `delay`. |
| `history_length` | 0 | When `> 0`, sensor `read()` returns the last `N` final measurements stacked along a new history axis, shape `(B, N, *return_shape)`; index 0 is the current step. |
| `noise` | 0.0 | Std-dev of zero-mean Gaussian, sampled once per step in `_apply_hardware_imperfections` and frozen into the return-space ring slot at capture time. Independent each step. |
| `bias` | 0.0 | Constant offset added at the sensor output stage. |
| `random_walk` | 0.0 | Std-dev of the random-walk step. The drift accumulator advances each step and is added to the output, then frozen into the return-space ring slot at capture time, so a delayed read sees the drift the sensor had at the moment it was captured. |
| `resolution` | 0.0 | Quantization step. Output values are rounded to multiples of this. |

`noise`, `bias`, `random_walk`, `resolution` are deliberately generic - they're imperfection *parameters*. `SimpleSensor._apply_hardware_imperfections` picks the "embedded sampler" interpretation laid out above (sensor-output stage). A direct `Sensor` subclass could interpret them differently or ignore them entirely (Camera does). Imperfections that need to propagate through the response model (e.g. genuine drift in the physical phenomenon being sensed) belong in an `_apply_physics_imperfections` override instead - that hook runs **before** `_apply_transform` so its contribution feeds the next step's recurrence.

### Why imperfections are baked in at capture time

The robot's `read()` is a memory lookup. Once a digitized value sits in the ring, the noise is frozen - reading the same slot later returns the same noisy value. This is what makes two `read()` calls within the same control-loop timestep return identical results, and what gives a delayed read the imperfection state the sensor had at the time of capture (random-walk drift from 100 ms ago is the drift the sensor actually had 100 ms ago, not the drift it has now).

Placing per-step hardware imperfections on the working buffer (not on the timeline ring) is what protects transform recurrence: a stateful response model (thermal dissipation, low-pass filter) reads previous slots of the timeline ring, which are clean of hardware noise. The return-space ring stores the post-everything snapshot AFTER `_apply_hardware_imperfections` has run for the current step, which is what later delay sampling reads.
