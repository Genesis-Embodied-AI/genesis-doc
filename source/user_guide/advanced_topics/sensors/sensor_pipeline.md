# The sensor pipeline

This page explains what happens between `scene.step()` and the value a sensor's `read()` hands back: how the sensor manager updates every sensor once per step, how sensors of different types share expensive computation, and how buffering makes `read()` a constant-time memory lookup rather than a fresh acquisition. It is the runtime companion to {doc}`custom_sensors`, which covers the hooks you override to add a sensor. For the user-facing side (attach a sensor, step, read a tensor) start with the {doc}`sensor overview </user_guide/getting_started/sensors/index>`.

## The mental model: read is a lookup, not an acquisition

A real robot does not pull a value through an analog wire on each control-loop iteration. Embedded firmware samples the hardware asynchronously at its own rate, processes the signal, and writes a digital snapshot into shared memory. The application's `read()` returns whatever snapshot is currently there. It does not trigger acquisition.

Genesis World models this exactly. The manager computes each sensor's value **once per `scene.step()`** and stores it; `read()` and `read_ground_truth()` are views into that storage. Two consequences follow, and the rest of the pipeline exists to preserve them:

- **Reads are idempotent within a step.** Two `read()` calls in the same timestep return the same value, because nothing recomputes between them. A controller, a logger, and a visualizer can all read the same sensor with no extra cost and no disagreement.
- **Imperfections are frozen at capture time.** Noise, bias, and drift are baked into the stored snapshot when it is written, not sampled at read time. A delayed read therefore returns the exact noisy value the sensor produced in the past, not a fresh sample.

## What the manager owns

The `SensorManager` (`genesis/engine/sensors/sensor_manager.py`) owns all sensor storage and drives the per-step update. Sensors themselves hold no per-step buffers; they contribute a slice of the manager's storage and a set of compute hooks.

Storage is organized so that every sensor of one class updates in a single batched pass. Sensors are grouped by class, and within a class each instance occupies a contiguous slice of that class's cache:

```python
# SensorManager.build: sort each class by entity so instances on the same
# entity occupy a contiguous slice, then assign each sensor its cache offset.
for sensors in self._sensors_by_type.values():
    sensors.sort(key=lambda s: s._options.entity_idx)
```

Because the slice is contiguous, one kernel processes the whole class. This is why dtype is class-uniform: every instance of a class shares one dtype so the per-class slice stays a single contiguous range in one buffer. Shape, by contrast, is per-instance, so options such as a raycaster's pattern or a temperature grid's resolution can change the returned shape without breaking batching.

Conceptually the manager keeps four kinds of storage:

- **Per-class return cache:** the buffer `read()` and `read_ground_truth()` view, in the return space the sensor declares. Shape `([n_envs,] class_cache_size)`.
- **Per-dtype intermediate cache:** the per-step working buffer that compute hooks read and write, before casting to return space.
- **Per-dtype timeline rings:** paired ground-truth and measured circular buffers holding pre-noise, post-transform values, so stateful filters can read previous steps without keeping their own state.
- **Per-class return-space rings:** paired circular buffers holding the finished snapshot at each past step. Delay sampling and history reads both source from here.

Rings and extra buffers cost memory, so the manager allocates them only when a sensor needs them. When a sensor applies no delay, no history, and no return-space cast, its return cache is a zero-copy alias of the intermediate cache and no rings are allocated at all:

```python
# SensorManager.build
needs_ring = cls_delay_depth > 1 or cls_max_history > 0 or pp_overridden
if needs_ring:
    ...  # allocate paired GT + measured return-space rings, distinct return cache
else:
    # Alias the return cache onto the intermediate slice: the per-step write is
    # already what read() should see.
    self._return_cache[sensor_cls] = self._intermediate_cache[intermediate_dtype][:, cls_slice]
```

## The per-step pipeline

`SensorManager.step` runs three phases in order:

```python
# SensorManager.step
for ring in self._measured_timeline_ring.values():
    ring.rotate()                       # free a fresh write slot before compute

for context in self._shared_contexts.values():
    context.update()                    # refresh each shared resource at most once

for sensor_cls, sensors in self._sensors_by_type.items():
    sensor_cls._update_shared_cache(...)  # one batched compute pass per class
    ...                                   # then post-process, ring write, delay sample
```

**Rotate the rings first.** The timeline rings must advance before compute, because the compute hook writes into slot 0 and stateful filters read the previous slots. Return-space rings rotate later, inside the per-class loop, so that during the cast step slot 0 still holds the previous step's finished output (a meaningful "last value") rather than stale data.

**Refresh shared contexts once.** Each shared resource is rebuilt at most once per step, before any sensor reads it, so several sensor types consuming the same context pay for it once. See the next section.

**Update each class, then finish it.** For each class the manager calls `_update_shared_cache` once, producing the ground-truth signal and the measured working buffer. It then casts both branches to return space via `_post_process`, writes the finished snapshots into the return-space ring, and delay-samples the measured ring into the return cache:

```python
# SensorManager.step, per class
gt_projected = sensor_cls._post_process(metadata, ground_truth_slice.T, gt_return_ring, is_measured=False)
measured_projected = sensor_cls._post_process(metadata, intermediate, measured_return_ring, is_measured=True)

gt_return_ring.rotate()               # rotate after _post_process reads, before writing
measured_return_ring.set(measured_projected)
gt_return_ring.set(gt_projected)

# Ground truth has no readout delay; the measured branch samples a stale slot.
self._ground_truth_return_cache[sensor_cls].copy_(gt_return_ring.at(0, copy=False))
sensor_cls._apply_delay(metadata, measured_return_ring, self._return_cache[sensor_cls])
```

Casting happens eagerly, once per branch per step, rather than lazily at read time. Eager casting gives the manager a real per-class buffer that every reader shares, keeps the cast count independent of how many consumers read the sensor, and lets stateful casts (a bandwidth filter, for instance) run exactly once per step.

The hooks named above (`_update_shared_cache`, `_post_process`, `_apply_delay`) belong to the sensor class, not the manager. `SimpleSensor` implements `_update_shared_cache` as a fixed sequence of finer hooks (raw signal, physics imperfections, transform, hardware imperfections) that concrete sensors override as needed. The order in which those fire and the buffers they touch are documented in {doc}`custom_sensors`.

## Shared context: sharing computation across sensor types

Some sensors need an expensive resource that is identical across sensor *types*. A raycaster and a raycast-based depth camera both cast against the same collision geometry; rebuilding that acceleration structure once per sensor would be wasteful. A **shared context** is that resource, built once and reused.

`SharedSensorContext` (`genesis/engine/sensors/base_sensor.py`) is the base class. A sensor type declares the context it consumes as a type parameter, and every type that names the same context class resolves to the one instance the manager owns:

```python
# The raycast BVH set is shared by the raycaster and the depth camera.
class RaycasterSensor(SimpleSensor[RaycasterOptions, RaycastContext, ...]):
    ...

class DepthCameraSensor(RaycasterSensor, Sensor[DepthCameraOptions, RaycastContext, ...]):
    ...
```

This is distinct from a sensor's *metadata*, which aggregates the per-instance state of one sensor type so a single kernel can run over all its instances. Metadata is a batching optimization that grows with the number of sensors; a context is a sharing optimization that stays O(1) in the number of sensors because it is one resource read by several types.

A context is purely an optimization, so it must never change results. Consistency stays the manager's responsibility through a strict lifecycle:

- **`activate`:** a consuming sensor calls this from its own `build`, when scene geometry is available. The first call constructs the resource; later calls are idempotent. A context that no sensor activates stays an empty shell and costs nothing.
- **`update`:** the manager calls this once per step, before the per-class loop, so every consumer sees the same refreshed resource. It is a no-op while inactive.
- **`reset` / `destroy`:** the manager drives these on `scene.reset()` and teardown.

Querying an inactive context raises rather than silently returning stale data, so a sensor cannot read a resource no one declared a need for.

## Ground truth versus measured

Every sensor carries two parallel branches through the pipeline, and exposes each through its own read method:

```python
# Sensor.read / Sensor.read_ground_truth
def read(self, envs_idx=None) -> DataT:
    return self._get_formatted_data(self._manager.get_cloned_from_cache(self), envs_idx)

def read_ground_truth(self, envs_idx=None) -> DataT:
    return self._get_formatted_data(self._manager.get_cloned_from_cache(self, is_ground_truth=True), envs_idx)
```

- **`read()`:** the measured value, with the sensor's imperfections applied and readout delay sampled in. This is what a controller trained for sim-to-real transfer should consume.
- **`read_ground_truth()`:** the noiseless, delay-free value from the same step, with identical shape. Use it for reward computation, logging, and debugging.

Both are pure views into per-class caches the manager already populated during `step()`; neither recomputes. The ground-truth branch keeps the raw simulated phenomenon and never sees readout delay, which is why its cache is filled straight from the current ring slot while the measured cache is delay-sampled.

## History and buffering

By default a sensor stores only the current snapshot. Set `history_length=N` and the manager keeps the last `N` finished snapshots so `read()` can return them stacked along a new axis:

```python
contact = scene.add_sensor(
    gs.sensors.Contact(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("FL_foot").idx_local,
        history_length=4,  # keep the last 4 snapshots; index 0 is the current step
    )
)
# ... after scene.build() and stepping ...
window = contact.read()  # shape ([n_envs,] 4, 1)
```

History reads always source from the per-class return-space ring, never the intermediate ring, because the return-space ring holds the finished post-everything snapshot at each step. The intermediate ring is in pre-noise space and would yield the wrong history:

```python
# SensorManager._gather_history
hist_idx = self._hist_idx_by_class[sensor_cls][:history_length]
ring = self._measured_return_timeline_ring[sensor_cls]  # or the GT ring
return ring.at(hist_idx).transpose(0, 1)
```

Delay and history share this ring. Delay reads a single stale slot; history reads a contiguous window of recent slots. The ring is sized to cover whichever demand is deeper.

## Reading a whole class at once

For bulk consumers (a logger recording every sensor, an observation vector for training) reading sensors one at a time is wasteful. `read_sensors` returns one tensor per sensor class in a single call, exposed on both the scene and the entity:

```python
data = scene.read_sensors()        # every sensor in the scene, grouped by class
data = robot.read_sensors()        # only the sensors attached to this entity
```

The result maps each sensor-type tag (`gs.sensors.types.<Name>`) to a tensor of shape `([n_envs,] [history,] class_cache_size)`; the history axis is present only for sensors configured with history. Unlike the per-sensor `read()`, which returns a view, `read_sensors` always allocates a fresh tensor by fancy-indexing the environment axis, so the caller is free to mutate the result without corrupting internal storage. The underlying `SensorManager.read_sensors` takes an `entity_idx` filter and an `is_ground_truth` flag that the public wrappers leave at their defaults.

## Options that shape the pipeline

Two options classes feed the pipeline. `SensorOptions` carries the timing knobs every sensor exposes; `SimpleSensorOptions` adds the imperfection parameters the `SimpleSensor` branch interprets at the readout stage. Each parameter's meaning is its effect inside the pipeline above:

| Option | Default | Effect |
|---|---|---|
| `delay` | 0.0 | Read offset into the measured return-space ring, in seconds. A delayed read returns the snapshot produced this many seconds ago, imperfections frozen at that step. |
| `jitter` | 0.0 | Random additive delay per environment, sampled uniformly in `[0, jitter)` each step. Must not exceed `delay`, and is capped at one `dt`. |
| `history_length` | 0 | When `> 0`, `read()` returns the last `N` finished snapshots stacked on a new axis; index 0 is the current step. |
| `noise` | 0.0 | Standard deviation of zero-mean Gaussian noise, sampled once per step and frozen into the snapshot. |
| `bias` | 0.0 | Constant offset added at the readout stage. |
| `random_walk` | 0.0 | Standard deviation of a random-walk step. The drift accumulates each step and is frozen into the snapshot, so a delayed read sees the drift the sensor had when the snapshot was captured. |
| `resolution` | 0.0 | Quantization step. Output values are rounded to multiples of this. |

`noise`, `bias`, `random_walk`, and `resolution` are generic imperfection parameters. `SimpleSensor` applies them at the readout stage on the per-step working buffer, never on the timeline ring, so a stateful filter's recurrence stays clean of readout noise. A sensor deriving directly from `Sensor` may interpret them differently or ignore them, as the camera sensors do.

## Sensors that bypass the pipeline

Not every sensor uses the ring pipeline. The camera sensors derive from `Sensor` directly, render lazily, and set `uses_ring_pipeline = False`. Because delay, jitter, and history all depend on the per-class return-space ring, a sensor that opts out cannot honor them, and the base class rejects those options at construction rather than silently ignoring them:

```python
# Sensor.__init__
if not self.uses_ring_pipeline:
    if options.delay > 0.0:
        gs.raise_exception(f"{type(self).__name__} does not support `delay`; ...")
```

The standard sensors (contact, contact force, IMU, joint torque, ranging, proximity, temperature, and the tactile family) all derive from `SimpleSensor` and use the full pipeline described here.

## See also

- {doc}`custom_sensors`: which hooks to override to add your own sensor type, and their shape and dtype contracts.
- {doc}`sensor overview </user_guide/getting_started/sensors/index>`: the user-facing attach-and-read workflow and the catalog of built-in sensors.
