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

This shapes every design decision in the pipeline:

- **Noise, drift, quantization, bias** are introduced by the embedded sampling layer **at snapshot time**. Once a digitized value sits in shared memory, the noise is baked in - reading the same cell later returns the same noisy value.
- **Delay (and its jitter)** is the staleness of the snapshot relative to "now". A sensor with `delay = D` (plus a random `jitter` drawn each step) means: at control-loop time `t`, the snapshot the robot reads was captured at time `t - D - jitter_t`. The snapshot was produced *with its imperfection state at the time of capture*; reading it later returns those imperfections unchanged. `delay` and `jitter` always travel together - jitter cannot exceed delay, and any non-zero jitter requires interpolation between adjacent ring slots.
- **Reads are idempotent within a step.** If a design implies they aren't, the abstraction is broken.
- **History reads** (`sensor.read(history_length=N)`) return the `N` most recent snapshots, each with the imperfection state that was present when it was produced.

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

`Sensor` is the minimal customization contract - a single abstract per-step compute method (`_update_shared_cache`), four spec accessors (`_get_return_format` / `_get_intermediate_format` as instance methods for shape; `_get_cache_dtype` / `_get_intermediate_dtype` as classmethods for dtype), a `_post_process` projection (identity by default), and a class-level capability flag (`uses_measured_pipeline: ClassVar[bool] = True`) telling the manager whether to allocate the measured-timeline ring for the class. `SimpleSensor` builds the standard pipeline on top, exposing four override hooks (`_update_raw_data`, `_update_current_timestep_data`, `_apply_transform`, `_apply_hardware_imperfections`) that concrete sensors override as needed. Signatures, contracts, and worked examples are in [Implementing Custom Sensors](custom_sensors.md). This page focuses on what those hooks *do* at runtime - the order in which they fire and the buffers they read and write.

## Per-step pipeline

```
[per-step, driven by SimpleSensor's orchestrator]

  _update_current_timestep_data
            │
            ├──► [GT branch]       ──► _apply_transform(data, timeline=None)
            │                                     │
            │                                     ▼
            │                          newest GT slot in the timeline ring
            │                          (current GT in intermediate space)
            │                                     │
            │                                     ▼
            │                          _post_process(GT intermediate)
            │                          (mirrored on the GT side so read_ground_truth()
            │                           is symmetric with read())
            │                                     │
            │                                     ▼
            │                          per-class GT return cache (return shape/dtype)
            │
            └──► [measured branch]  ──► _apply_transform(data, timeline=ring)
                                                 │ (transform on both branches; filter portion
                                                 │  gated by `if timeline is not None` reads earlier slots)
                                                 ▼
                                       _apply_hardware_imperfections(current snapshot)
                                                 │ (noise/bias/random_walk/resolution baked in
                                                 │  at snapshot time - PRE-delay)
                                                 ▼
                                       newest measured slot in the timeline ring
                                       (current snapshot in intermediate space)
                                                 │
                                                 ▼
                                       delay sampling: read stale slot at (delay + jitter) steps back
                                       (per-env offsets; reads STALE snapshots with their
                                        original imperfection state)
                                                 │
                                                 ▼
                                       _post_process(intermediate cache)
                                       (eager, once per step; per-class classmethod)
                                                 │
                                                 ▼
                                       per-class measured return cache (return shape/dtype)

[per-step refresh, only for sensor classes with overridden `_post_process` AND `history_length > 0`]

  current step's eager `_post_process` result is written to slot 0 of a per-class return-space ring
  (correct for stateful `_post_process`: each historical slot keeps the projection state at its capture time)

[read paths — idempotent within a step]

  Sensor.read()                          ─► view into latest snapshot for this sensor
  Sensor.read_ground_truth()             ─► same, ground-truth side
  Sensor.read(history_length=N)          ─► fresh tensor with the last N snapshots, gathered from the return-space
                                            ring (overridden `_post_process`) or the intermediate ring (identity)
  SensorManager.read_sensors()           ─► fresh tensor per class; per-class return cache (no history) or ring
                                            gather (history).
```

### The intermediate-vs-return separation

The pipeline operates in **intermediate space** throughout (delay sampling, transform, filters, hardware imperfections). Casting (bool threshold, clamp, mask, deadband) lives in `_post_process`, which is applied **eagerly** once per step at the end of the orchestrator. This populates a per-class **return cache** in the return space (shape declared by `_get_return_format`, dtype by `_get_cache_dtype`).

The separation is **structural, not aesthetic**. `_apply_transform(timeline=...)` lets filter overrides read previous slots of the timeline ring (e.g. `timeline.at(1)` for the previous frame); those slots must be in the **same data space** as the `data` argument the override receives, otherwise the filter mixes apples and oranges and silently produces wrong output. So the timeline ring holds intermediate-space values; the return cache is a separate buffer in the return space.

When `_post_process` is identity, the manager allocates a single buffer and aliases `return_cache` as a view of the intermediate slice - no extra storage. When `_post_process` is overridden (ContactSensor: float to bool; ContactForceSensor: clamp + masked_fill), the return cache is a distinct buffer. The author signals this distinction by overriding `_get_intermediate_format` and/or `_get_intermediate_dtype` (a no-op override returning the return-space value is acceptable when shape and dtype coincide).

### Why shape is per-instance and dtype is class-uniform

`_get_return_format` and `_get_intermediate_format` are instance methods. Sensor options are free to affect the returned shape - `Raycaster.pattern.return_shape`, `Camera.res`, `Proximity.probe_local_pos`, `TemperatureGrid.grid_size`, etc. This is supported by design; the manager accumulates each instance's contribution into the per-class slice when sizing buffers.

`_get_cache_dtype` and `_get_intermediate_dtype` are classmethods. Dtype is class-uniform - one dtype per sensor class, shared by every instance. This is a load-bearing invariant of the manager: the per-class slice into the per-dtype intermediate buffer must be contiguous. If two instances of the same class had different dtypes, the per-class slice would no longer be a single contiguous range in one buffer, the per-class metadata fields (`ContactSensorMetadata.thresholds`, `IMUSharedMetadata.magnetic_field_vector`, ...) would have to be split, and the once-per-step `_update_shared_cache` / `_apply_transform` contract would degenerate into multiple per-(class, dtype) sub-batches. Use two different sensor classes if you need different dtypes.

### Why `_post_process` is eager (write-time), not lazy (read-time)

Three reasons:

1. **Stateful post-processing is well-defined.** Because the manager calls `_post_process` exactly once per simulation step, the override may carry per-call state and advance it deterministically. This makes `_post_process` a natural home for software-level signal processing layered on top of the raw measurement - complementary filter, Mahony filter, Kalman filter, IMU quaternion estimator. A lazy (read-time) placement would re-invoke the projection N times per step for N consumers (controller + logger + visualization), advancing any internal state by N instead of 1 - corrupting the estimator's time series.
2. **Real per-class return storage.** Without eager projection, the per-class return cache wouldn't exist and `_post_process` overrides would have to allocate fresh tensors at every read. Eager placement means the manager owns a real per-class buffer of post-processed values that every read path (single sensor or bulk class read) gathers from.
3. **Amortized cost.** A typical control loop reads each sensor once per step from the controller, again from a logger, again from visualization. Eager projection runs the post-process once per step regardless of read fan-out. Lazy projection would re-run it per consumer.

## Storage scopes and the per-step loop

The manager owns all storage. Conceptually there are three scopes:

- **Per-dtype intermediate storage** - one buffer per data type used by sensors with that dtype, holding pipeline-internal values that hooks like `_apply_transform` read and write. A contiguous slice within this buffer belongs to each sensor class.
- **Per-class return storage** - one buffer per sensor class, in the return space declared by `_get_return_format` / `_get_cache_dtype`. When `_post_process` is the identity default the return view aliases into the intermediate slice (no extra memory); when `_post_process` is overridden it is a distinct buffer that the eager projection writes into.
- **Per-dtype timeline ring** - circular buffer of recent intermediate-space snapshots. The ground-truth ring is sized by the deepest `delay` and `history_length` requirement among sensors of that dtype; with all defaults it collapses to a single slot. The measured ring is allocated whenever any sensor class declares `uses_measured_pipeline = True` (the default; only sensors that bypass the standard orchestrator opt out). The two sides share their rotation index so a single rotation step advances both.
- **Per-class return-space ring** (rare) - allocated only for classes whose `_post_process` is overridden AND that have `history_length > 0`. Each step the eager `_post_process` snapshot is written to slot 0 of this ring, so history reads can pull post-processed values directly. For sensors with identity `_post_process` (most of them) the intermediate ring already holds return-space values, and no extra ring is needed.

Per simulation step the manager:

1. Rotates the timeline rings that exist, freeing the oldest slot to write the new snapshot.
2. For each sensor class, invokes `_update_shared_cache` once, passing the per-class slices of the intermediate cache, the measured timeline ring (or `None` if the class opted out), and the per-class return cache. The hook is responsible for producing the ground-truth signal and the measured snapshot in those buffers.
3. Mirrors the eager `_post_process` projection on the ground-truth side so that `read_ground_truth()` is symmetric with `read()`.
4. For sensor classes whose `_post_process` is overridden AND that declare `history_length > 0`, writes the freshly post-processed ground-truth and measured snapshots into the per-class return-space ring. Identity-projection classes need no extra ring (the intermediate ring is already in return space).

`read_sensors(envs_idx=...)` always returns a fresh tensor per class, independent of internal sensor storage. Non-history reads gather the current snapshot from the per-class return cache; history reads gather the last `N` snapshots from the appropriate ring. The caller is free to mutate the result.

## Options and their pipeline semantics

Two options classes feed the pipeline. `SensorOptions` carries the time-related knobs that every sensor exposes; `SimpleSensorOptions(SensorOptions)` adds the imperfection parameters that the SimpleSensor branch interprets. Camera, deriving from `Sensor` directly, only sees the time-related fields. The semantic of every parameter is its effect inside the pipeline diagram above:

| Option | Default | Where it acts |
|---|---|---|
| `delay` | 0.0 | Sets the read offset into the measured ring (seconds, snapshot age). |
| `jitter` | 0.0 | Random additive delay per env, sampled `Uniform[0, jitter)` each step. Must be <= `delay`. |
| `interpolate` | False | Linear interpolation between adjacent ring slots for fractional delays. Required when `jitter > 0`. |
| `history_length` | 0 | When `> 0`, sensor `read()` returns the last `N` measurements (flat-2 shape `[B, N * cache_size]`). |
| `noise` | 0.0 | Std-dev of zero-mean Gaussian, added to the snapshot at PRE-delay snapshot time. Independent each step. |
| `bias` | 0.0 | Constant offset added at snapshot time. |
| `random_walk` | 0.0 | Std-dev of the random-walk step. The drift accumulator advances each step and is added at production time, so a delayed read returns the drift state from when the snapshot was captured. |
| `resolution` | 0.0 | Quantization step. Snapshot values are rounded to multiples of this. |

`noise`, `bias`, `random_walk`, `resolution` are deliberately generic - they're imperfection *parameters*. `SimpleSensor._apply_hardware_imperfections` is the one that picks the "embedded sampler" interpretation laid out above. A direct `Sensor` subclass could interpret them differently or ignore them entirely (Camera does).

### Why noise lives at snapshot time, not read time

If noise were applied at read time (e.g. fresh per `read()` call), two `read()` calls in the same control-loop timestep would return different values. That breaks the embedded-sampler abstraction: once a digitized value is in shared memory, the noise is baked in - the user code that reads it doesn't re-sample. The pipeline places noise where the embedded sampler actually introduces it.

This also makes `random_walk` (drift) physically correct: a snapshot captured 100 ms ago shows the drift state the sensor had 100 ms ago, not the drift the sensor has now.
