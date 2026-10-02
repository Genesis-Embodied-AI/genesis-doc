# Sensor pipeline

This page explains what happens between `scene.step()` and the value a sensor's `read()` hands back: how the sensor manager updates every sensor once per step, how sensors of different types share expensive computation, and how buffering makes `read()` a constant-time memory lookup rather than a fresh acquisition. It is the runtime companion to {doc}`custom_sensors`, which covers the hooks you override to add a sensor. For the user-facing side (attach a sensor, step, read a tensor) start with the {doc}`sensor overview </user_guide/sensing/index>`.

## Read is a lookup, not an acquisition

A real robot does not pull a value through an analog wire on each control-loop iteration. Embedded firmware samples the hardware asynchronously at its own rate, processes the signal, and writes a digital snapshot into shared memory. The application's `read()` returns whatever snapshot is currently there. It does not trigger acquisition.

Genesis World models this exactly. The sensor array computes each sensor's value **once per `scene.step()`** and stores it; `read()` and `read_ground_truth()` copy the snapshot out of that storage. Cameras are the one exception: they render on read and keep the frames (see the last section). Two consequences follow, and the rest of the pipeline exists to preserve them:

- **Reads are idempotent within a step.** Two `read()` calls in the same timestep return the same value, because nothing recomputes between them. A controller, a logger, and a visualizer can all read the same sensor with no extra cost and no disagreement.
- **Imperfections are frozen at capture time.** Noise, bias, and drift are baked into the stored snapshot when it is written, not sampled at read time. A delayed read therefore returns the exact noisy value the sensor produced in the past, not a fresh sample.

## Handles, arrays and the manager

A sensor type is two classes. The *handle* (`Sensor`) is what `scene.add_sensor(...)` returns: it holds the options of one sensor and its index among the sensors of its type, and every method on it delegates to the array with that index. The *array* (`SensorArray`) is one object per sensor type and scene: it owns every tensor of the type and computes one step of data for all its sensors at once, the way a solver owns and steps every entity of its kind.

The `SensorManager` (`genesis/engine/sensors/sensor_manager.py`) constructs the array of a type when the first sensor of that type is added, hands it every handle, then drives it like a solver: `build` once the scene is built, `step` once per `scene.step()`, `reset` and `destroy` with the scene.

Within an array each sensor occupies a contiguous slice of one flat cache, the sensors sorted by entity so those on the same entity are contiguous too:

```python
# SensorArray.build: sort the sensors by entity, assign each its index, then lay their columns end to end.
self._sensors.sort(key=lambda sensor: sensor._options.entity_idx)
for i_s, sensor in enumerate(self._sensors):
    sensor._idx = i_s
```

Because the slice is contiguous, one kernel processes the whole type. This is why dtype is uniform over a type: every sensor of a type shares one dtype so the cache stays a single contiguous buffer. Shape, by contrast, is per-sensor, so options such as a raycaster's pattern or a temperature grid's resolution can change the returned shape without breaking batching.

Conceptually an array keeps four kinds of storage, every buffer and every ring slot of shape `(B, cols)` with the batch dimension first:

- **Return caches:** the buffers `read()` and `read_ground_truth()` view, in the return space the type declares.
- **Working buffers:** the ground-truth cache and the intermediate cache the compute hooks read and write, before casting to return space.
- **Timeline rings:** paired ground-truth and measured circular buffers holding pre-noise, post-transform values, so stateful filters can read previous steps without keeping their own state.
- **Return-space rings:** paired circular buffers holding the finished snapshot at each past step. Delay sampling and history reads both source from here.

Rings and extra buffers cost memory, so an array allocates them only when a sensor needs them. When no sensor of the type applies a delay, a history, or a return-space cast, the return caches are zero-copy aliases of the working buffers and no return-space ring is allocated at all:

```python
# SensorArray.build
if delay_depth > 1 or max_history > 0 or is_post_process_overridden:
    ...  # allocate paired GT + measured return-space rings and distinct return caches
else:
    # The return caches alias the working buffers, whose per-step write is directly visible to `read`
    self._return_cache = self._intermediate_cache
    self._ground_truth_return_cache = self._ground_truth_cache
```

## Per-step pipeline

`SensorManager.step` refreshes the shared contexts, then steps every array:

```python
# SensorManager.step
for context in self._shared_contexts.values():
    context.update()                    # refresh each shared resource at most once
for array in self._arrays.values():
    array.step()                        # one batched compute pass per type
```

**Refresh shared contexts once.** The manager rebuilds each shared resource at most once per step, before any array reads it, so several sensor types consuming the same context pay for it once. See the next section.

**Step each array.** `SensorArray.step` rotates the timeline rings, computes the caches, then finishes the step:

```python
# SensorArray.step
self._measured_timeline.rotate()      # free a fresh write slot before compute
self._update_cache()                  # the ground truth and the measured working buffer of every sensor
if self._measured_return_timeline is None:
    return                            # no delay, history or cast: the caches are what read() sees
measured_projected = self._post_process(self._intermediate_cache, self._measured_return_timeline, is_measured=True)
ground_truth_projected = self._post_process(self._ground_truth_cache, self._ground_truth_return_timeline, is_measured=False)
self._ground_truth_return_timeline.rotate()   # rotate after _post_process reads, before writing
self._measured_return_timeline.set(measured_projected)
self._ground_truth_return_timeline.set(ground_truth_projected)
# Ground truth has no readout delay; the measured branch samples a stale slot.
self._ground_truth_return_cache.copy_(self._ground_truth_return_timeline.at(0, copy=False))
self._apply_delay(self._measured_return_timeline, self._return_cache)
```

The timeline rings rotate before compute, because the compute hook writes into slot 0 and stateful filters read the previous slots. The return-space rings rotate later, so that during the cast step slot 0 still holds the previous step's finished output (a meaningful "last value") rather than stale data.

Casting happens eagerly, once per branch per step, rather than lazily at read time. Eager casting gives the array a real buffer that every reader shares, keeps the cast count independent of how many consumers read the sensor, and lets stateful casts (a bandwidth filter, for instance) run exactly once per step.

`SimpleSensorArray` implements `_update_cache` as a fixed sequence of finer hooks (raw signal, physics imperfections, transform, hardware imperfections) that concrete arrays override as needed. {doc}`custom_sensors` documents the order in which those fire and the buffers they touch.

## Shared context: sharing computation across sensor types

Some sensors need an expensive resource that is identical across sensor *types*. A raycaster and a raycast-mode tactile sensor both cast against the same collision geometry; rebuilding that acceleration structure once per type would be wasteful. A **shared context** is that resource, built once and reused.

`SharedSensorContext` (`genesis/engine/sensors/base_sensor.py`) is the base class. An array fetches the context it reads from the manager in its `build`, and every array asking for the same context class gets the one instance the manager owns, constructed on the first request:

```python
# The raycast BVH set is shared by the raycasters and the raycast-mode tactile sensors.
class RaycasterSensorArray(KinematicSensorArrayMixin, SimpleSensorArray[RaycasterOptions, RaycasterReturnType]):
    def build(self):
        super().build()
        self._raycast = self._manager.get_context(RaycastContext)
        self._raycast.activate()
```

This is distinct from the array itself, which aggregates the per-sensor state of one type so a single kernel can run over all its sensors. An array is a batching optimization that grows with the number of sensors; a context is a sharing optimization that stays O(1) in the number of sensors because it is one resource read by several types.

A context is purely an optimization, so it must never change results. Consistency stays the manager's responsibility through a strict lifecycle:

- **`activate`:** a consuming array calls this from its own `build`, when scene geometry is available. The first call constructs the resource; later calls are idempotent. A context that no array activates stays an empty shell and costs nothing.
- **`update`:** the manager calls this once per step, before the arrays step, so every consumer sees the same refreshed resource. It is a no-op while inactive.
- **`reset` / `destroy`:** the manager drives these on `scene.reset()` and teardown.

Querying an inactive context raises rather than silently returning stale data, so an array cannot read a resource no one declared a need for.

## Ground truth versus measured

Every sensor carries two parallel branches through the pipeline, and exposes each through its own read method on the handle:

```python
# Sensor.read / Sensor.read_ground_truth
def read(self, envs_idx=None) -> DataT:
    return self._array.read(self._idx, envs_idx)

def read_ground_truth(self, envs_idx=None) -> DataT:
    return self._array.read(self._idx, envs_idx, is_ground_truth=True)
```

- **`read()`:** the measured value, with the sensor's imperfections applied and readout delay sampled in. This is what a controller trained for sim-to-real transfer should consume.
- **`read_ground_truth()`:** the noiseless, delay-free value from the same step, with identical shape. Use it for reward computation, logging, and debugging.

Both copy out of the caches the array already populated during `step()`; neither recomputes. The ground-truth branch keeps the raw simulated phenomenon and never sees readout delay, which is why the array fills its cache straight from the current ring slot and delay-samples the measured one.

## History and buffering

By default a sensor stores only the current snapshot. Set `history_length=N` and the array keeps the last `N` finished snapshots so `read()` can return them stacked along a new axis:

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

History reads always source from the return-space ring, never the intermediate ring, because the return-space ring holds the finished post-everything snapshot at each step. The intermediate ring is in pre-noise space and would yield the wrong history:

```python
# SensorArray._gather_history
ring = self._ground_truth_return_timeline if is_ground_truth else self._measured_return_timeline
return ring.at(self._history_idx[:history_length]).transpose(0, 1)
```

Delay and history share this ring. Delay reads a single stale slot; history reads a contiguous window of recent slots. The ring is sized to cover whichever demand is deeper.

## Reading a whole type at once

For bulk consumers (a logger recording every sensor, an observation vector for training) reading sensors one at a time is wasteful. `read_sensors` returns one tensor per sensor type in a single call, exposed on both the scene and the entity:

```python
data = scene.read_sensors()        # every sensor in the scene, grouped by type
data = robot.read_sensors()        # only the sensors attached to this entity
```

The result maps each sensor-type tag (`gs.sensors.types.<Name>`) to a tensor of shape `([n_envs,] [history,] type_cache_size)`; the history axis is present only for sensors configured with history. Like the per-sensor `read()`, `read_sensors` returns a fresh tensor, so the caller is free to mutate the result without corrupting internal storage. The underlying `SensorManager.read_sensors` takes an `entity_idx` filter and an `is_ground_truth` flag that the public wrappers leave at their defaults, and asks each array for its slice through `SensorArray.read_all`.

## Options that shape the pipeline

Two options classes feed the pipeline. `SensorOptions` carries the timing knobs every sensor exposes; `SimpleSensorOptions` adds the imperfection parameters the `SimpleSensorArray` branch interprets at the readout stage. Each parameter's meaning is its effect inside the pipeline above:

| Option | Default | Effect |
|---|---|---|
| `delay` | 0.0 | Read offset into the measured return-space ring, in seconds. A delayed read returns the snapshot produced this many seconds ago, imperfections frozen at that step. |
| `jitter` | 0.0 | Random additive delay per environment, sampled uniformly in `[0, jitter)` each step. Must not exceed `delay`, and is capped at one `dt`. |
| `history_length` | 0 | When `> 0`, `read()` returns the last `N` finished snapshots stacked on a new axis; index 0 is the current step. |
| `noise` | 0.0 | Standard deviation of zero-mean Gaussian noise, sampled once per step and frozen into the snapshot. |
| `bias` | 0.0 | Constant offset added at the readout stage. |
| `random_walk` | 0.0 | Standard deviation of a random-walk step. The drift accumulates each step and is frozen into the snapshot, so a delayed read sees the drift the sensor had when the snapshot was captured. |
| `resolution` | 0.0 | Quantization step. Output values are rounded to multiples of this. |

`noise`, `bias`, `random_walk`, and `resolution` are generic imperfection parameters. `SimpleSensorArray` applies them at the readout stage on the per-step working buffer, never on the timeline ring, so a stateful filter's recurrence stays clean of readout noise. An array deriving directly from `SensorArray` may interpret them differently or ignore them, as the camera arrays do.

## Sensors that bypass the pipeline

Not every sensor uses the ring pipeline. The camera arrays derive from `SensorArray` directly, render on read, and set `has_ring_pipeline = False`: they own their frames, keep them between reads, and take none of the per-step buffers. Because delay, jitter, and history all depend on the return-space ring, a type that opts out cannot honor them, and the array rejects those options when the sensor is added rather than silently ignoring them:

```python
# SensorArray.add_sensor
if not self.has_ring_pipeline:
    for name, value in (("delay", options.delay), ("jitter", options.jitter), ("history_length", options.history_length)):
        if value > 0:
            gs.raise_exception(f"{type(sensor).__name__} does not support `{name}`; got {name}={value}.")
```

The standard sensors (contact, contact force, IMU, joint torque, ranging, surface distance, temperature, and the tactile family) all derive from `SimpleSensorArray` and use the full pipeline described here.

## See also

- {doc}`custom_sensors`: which hooks to override to add your own sensor type, and their shape and dtype contracts.
- {doc}`sensor overview </user_guide/sensing/index>`: the user-facing attach-and-read workflow and the catalog of built-in sensors.
