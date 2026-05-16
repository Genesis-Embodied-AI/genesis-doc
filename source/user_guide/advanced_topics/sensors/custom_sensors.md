# 🧰 Implementing Custom Sensors

This page is a guide for advanced users who want to add their own sensor type. It is the writer's counterpart to [Sensor Pipeline](sensor_pipeline.md), which describes how the pipeline executes at runtime; here we focus on which hooks to override, what shape/dtype contracts they must satisfy, and how the automatic plugin registration works.

In almost every case, derive from `SimpleSensor` and override **only the hooks you need**. Deriving directly from `Sensor` is reserved for sensors that bypass the standard pipeline entirely (the built-in cameras do this).

## What you write to add a sensor

To add a new sensor you contribute four artifacts:

| Artifact | Where | Role |
|---|---|---|
| `<Name>` (an options class) | `genesis/options/sensors/<name>.py` (or your plugin package) | Public, user-facing dataclass that carries every per-sensor parameter. Inherits `SimpleSensorOptions` (or the appropriate mixin). Generic-parameterized with the sensor class as a forward reference. |
| `<Name>SharedMetadata` | next to the sensor implementation | Per-sensor-class runtime state shared across every instance of this sensor in the scene. Inherits `SimpleSensorMetadata` (or `SharedSensorMetadata` for non-Simple sensors). |
| `<Name>Sensor` | next to the sensor implementation | The sensor class itself. Inherits `SimpleSensor[<Name>, <Name>SharedMetadata]` and overrides `_get_return_format` (instance, shape), `_get_cache_dtype` (classmethod, dtype), `_update_raw_data`, plus optionally `_update_current_timestep_data`, `_apply_physics_imperfections`, `_apply_transform`, `_apply_hardware_imperfections`, `_post_process` (paired with `_get_intermediate_format` and/or `_get_intermediate_dtype`). |
| (optional) a `NamedTuple` data class | next to the sensor implementation | If your sensor returns multiple tensors (e.g. IMU returns `lin_acc`, `ang_vel`, `mag`), declare a NamedTuple and pass it as the third type parameter: `SimpleSensor[<Name>, <Name>SharedMetadata, <Name>Data]`. |

Genesis pairs an options class with its sensor class automatically as soon as both modules have been imported - the user only ever creates the options instance and passes it to `scene.add_sensor(...)`.

## Automatic registration (the plugin mechanism)

Sensors do not need to be registered manually. Defining a `Sensor` subclass parameterized with its options class is enough; the framework records the pairing the moment the class body runs.

That gives you two supported placements:

- **In-tree (built-in sensors)** - options in `genesis/options/sensors/*.py`, sensor in `genesis/engine/sensors/*.py`. Both are imported through the package `__init__` already.
- **Out-of-tree (third-party plugins)** - put `MyOptions` and `MySensor` in **sibling submodules of the same Python package**:

  ```
  my_sensor_plugin/
    __init__.py
    options.py     # class MyOptions(SimpleSensorOptions["MySensor"]): ...
    sensor.py      # class MySensor(SimpleSensor[MyOptions, MyMetadata]): ...
  ```

  As long as your code imports `my_sensor_plugin.options` somewhere before constructing `MyOptions()`, Genesis will lazily import the sibling `my_sensor_plugin.sensor` module on the first call to `scene.add_sensor(MyOptions(...))` and the pairing resolves transparently.

## Picking the right base class

| Base | When to use |
|---|---|
| `SimpleSensor[OptionsT, MetadataT]` | Almost always. Per-step pipeline (raw -> physics imperfections -> transform -> hardware imperfections -> post-process -> delay sampling). |
| `SimpleSensor[OptionsT, MetadataT, DataT]` | Same as above, but `read()` returns an instance of `DataT` (a `NamedTuple`) instead of a single tensor. IMU is the canonical example. |
| `BaseCameraSensor[OptionsT]` | Camera-style sensors that render an RGB image lazily on `read()` (rasterizer, ray tracer, batched renderer, custom renderer). Inherits the lazy-render lifecycle, link-attachment with `pos/lookat/up`, and the `_post_process`/`_get_*` plumbing from `Sensor`. See [Camera-style sensors via BaseCameraSensor](#camera-style-sensors-via-basecamerasensor) below. |
| `Sensor[OptionsT, MetadataT]` | Only when neither standard pipeline applies. Overriding at this level means implementing `_update_shared_cache` yourself, and (if your implementation does not use the timeline rings) setting the class attribute `uses_ring_pipeline = False` to skip ring allocation. Also the right choice when you want **full kernel control** and need a single kernel pass to write both the ground-truth slice and the measured-timeline slot with internal noise (see [Kernel-internal physics noise](#kernel-internal-physics-noise) below). |

For mixins, the convention is:

- `KinematicSensorOptionsMixin` for sensors attached to a `KinematicEntity` (or anything kinematic-only).
- `RigidSensorOptionsMixin` for sensors that require rigid-body physics (contact, IMU, tactile, ...). Combine with `SimpleSensorOptions` via multiple inheritance.
- On the sensor side, `RigidSensorMixin` / `RigidSensorMetadataMixin` give you a typed `solver` field and the links bookkeeping you typically need.

## The hooks of `SimpleSensor`

All hooks are `@classmethod`s. They receive `shared_metadata` (the per-sensor-class state container) and the buffers they must populate. Hooks are called once per simulation step for the whole class at once - never per sensor instance, never per environment.

### Required overrides

#### `_get_return_format(self) -> tuple[...]`

Instance method returning the **shape** of what `read()` returns. Shape is per-instance by design: sensor options may legitimately determine the returned shape (`Raycaster.pattern.return_shape`, `Camera.res`, `Proximity.probe_local_pos`, etc.).

```python
def _get_return_format(self) -> tuple[int, ...]:
    return (3,)
```

Conventions:

- `(N,)` for a single per-sensor tensor of `N` scalars.
- `((3,), (3,), (3,))` (tuple of tuples) for a multi-tensor return (NamedTuple data class). Must match the fields of the `DataT` you specified in the generic parameter.

#### `_get_cache_dtype(cls) -> torch.dtype`

Classmethod returning the **dtype** of what `read()` returns. Dtype is class-uniform: a single dtype shared by every instance of the sensor class. This is a load-bearing invariant of the manager - the per-class slice into the per-dtype intermediate buffer must be contiguous, so all instances of a class must share one dtype. If you need different dtypes for different instances, use two different sensor classes.

```python
@classmethod
def _get_cache_dtype(cls) -> torch.dtype:
    return gs.tc_float
```

The split between an instance method for shape and a classmethod for dtype is deliberate: it lets the manager resolve the per-class dtype without instantiating any sensor, while still allowing the per-instance shape to depend on options.

#### `_update_raw_data(cls, shared_metadata, raw_data_T)`

The sensor-specific kernel that computes the **ground-truth** value of every sensor of this class for the current timestep. The output buffer `raw_data_T` has shape `(cols, B)` - **column-major**, batch dimension last - to be C-contiguous for per-class row slices when other sensors write to the same intermediate cache. Always populate the buffer in place.

```python
@classmethod
def _update_raw_data(cls, shared_metadata, raw_data_T):
    pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)   # (B, N, 3)
    raw_data_T.copy_(pos.reshape(pos.shape[0], -1).T)                       # (3*N, B)
```

This is the only abstract hook of `SimpleSensor`. `_get_return_format` and `_get_cache_dtype` from the base `Sensor` are also required (see above). Everything else has a sensible default.

### Optional overrides

#### `_apply_transform(cls, shared_metadata, data, timeline, *, is_measured)`

Apply a coordinate transform and/or a stateful response model, in place, on `data` (a batch-first view `[B, cache_size, ...]`). Called twice per step: once on the ground-truth branch with the GT timeline ring (`is_measured=False`), once on the measured branch with the measured timeline ring (`is_measured=True`). Both rings hold post-transform, **PRE-hardware-imperfection** values, so recurrence reads (`timeline.at(1)` and earlier) are always clean of hardware noise.

- The coordinate-transform portion runs unconditionally on both branches.
- The response-model portion (e.g. thermal dissipation, exponential moving average, low-pass) reads previous slots via `timeline.at(1)`, `timeline.at(2)`, etc. The current write target is `data` (alias of `timeline.at(0)`); do not double-write.
- **Aliasing note:** `data is timeline.at(0, copy=False)` - they refer to the same memory. Use whichever reads more naturally.
- Gate any sensor-element-specific pre-acquisition effect (RC time constant, mechanical bandwidth - things that belong to the sensor element and must not appear in GT) on `if is_measured:`. Branch-symmetric effects skip the gate.

```python
@classmethod
def _apply_transform(cls, shared_metadata, data, timeline, *, is_measured):
    # Coordinate transform: always runs on both branches.
    data.copy_(transform_by_quat(data, shared_metadata.world_to_local_quat))

    # Sensor-element response model (RC time constant). Measured-only because GT must return the underlying
    # physical phenomenon untouched by the sensor element.
    if is_measured:
        prev = timeline.at(1)
        data.mul_(1 - shared_metadata.alpha).add_(prev, alpha=shared_metadata.alpha)
```

The default of running on both branches is what you want for any frame change or coordinate transform. Use the `is_measured` gate when the response is a property of the sensor element itself. For post-acquisition stateful effects (DSP filtering at the sensor output) use `_post_process` with `is_measured` instead - it sees the per-class return-space ring.

#### `_post_process(cls, shared_metadata, tensor, timeline, *, is_measured) -> torch.Tensor`

Projection from intermediate space to return space. Override when the user-facing output type and/or shape differs from the pipeline-internal representation: bool threshold on `ContactSensor`, deadband + saturation on `ContactForceSensor`, etc. Return the post-cast tensor; the manager writes it into slot 0 of the per-class return-space ring, and (on the measured branch) then delay-samples that ring into the user-visible return cache.

Called once per branch per step. `tensor` is the full per-class intermediate cache in intermediate space (the current step's input). `timeline` is the per-class return-space ring; it is rotated AFTER this call returns, so inside the override `timeline.at(0)` is the previous step's post-output, `timeline.at(1)` is the step before that, and so on - stateful overrides (e.g. a sensor-element bandwidth filter on the measured branch) use these for recurrence. `is_measured` distinguishes branches (`True` on the measured call, `False` on the GT call) so an override can apply readout-stage contributions on only one side.

Designed for cast / clamp / threshold / mask / deadband / simple reductions and (optionally) stateful post-acquisition DSP responses (anti-alias filter, decimation memory) that operate in **return space** on the projected signal. Pre-acquisition effects (RC filter on the underlying physical signal, mechanical bandwidth of the sensor element) belong in `_apply_transform` with `is_measured=True` instead - they need the intermediate-space ring. Stateless overrides do not need to touch `timeline` or `is_measured`:

```python
@classmethod
def _post_process(cls, shared_metadata, tensor, timeline, *, is_measured):
    return tensor > shared_metadata.thresholds
```

If you override `_post_process` you **must** also override `_get_intermediate_format` and/or `_get_intermediate_dtype`. The pipeline enforces this at class-definition time:

```
TypeError: <Name>Sensor overrides `_post_process` but neither `_get_intermediate_format` nor
`_get_intermediate_dtype`; declare the intermediate buffer explicitly (no-op override returning
the return-space value is acceptable when they coincide).
```

The reason is structural, not aesthetic: the intermediate buffer must be a **distinct** buffer regardless of whether its shape and dtype happen to coincide with the return space. The timeline ring is in intermediate space; mixing data spaces breaks `_apply_transform` filter overrides that read previous slots. When the projection genuinely preserves shape and dtype (ContactForceSensor: clamp + masked_fill), override one of the intermediate methods as a no-op returning the return-space value - the override declaration is the explicit acknowledgement that the intermediate is a distinct buffer.

See [the intermediate-vs-return separation section](sensor_pipeline.md#the-intermediate-vs-return-separation) for the full structural rationale.

#### `_get_intermediate_format(self) -> tuple[...]`

Instance method returning the shape of the **pipeline-internal** buffer (transform, physics imperfections, hardware imperfections all happen in this space; `_post_process` projects out of it into return space). Defaults to `_get_return_format()`. Override together with `_post_process` whenever your projection changes shape, or as a no-op acknowledgement when only `_get_intermediate_dtype` would otherwise differ.

```python
def _get_intermediate_format(self) -> tuple[int, ...]:
    return self._get_return_format()  # no-op when shape coincides with return
```

#### `_get_intermediate_dtype(cls) -> torch.dtype`

Classmethod returning the dtype of the pipeline-internal buffer. Defaults to `_get_cache_dtype()`. Override together with `_post_process` when the projection changes dtype (e.g. ContactSensor: float intermediate, bool return).

```python
@classmethod
def _get_intermediate_dtype(cls) -> torch.dtype:
    return gs.tc_float  # float kernel output; bool projection in `_post_process`
```

When `_get_intermediate_format` and `_get_intermediate_dtype` both default, `_post_process` is identity, **and** no sensor in the class declares `delay > 0` or `history_length > 0` (the common case for most no-op sensors), the manager allocates **one** buffer and aliases the return cache as a view of the intermediate cache - no extra memory, no copy. Any of those triggers - overriding `_post_process`, non-zero delay, non-zero history - causes the manager to allocate a separate per-class return cache and a per-class return-space ring to back delay sampling and history reads.

#### `_apply_physics_imperfections(cls, shared_metadata, measured_slot_0, timeline)`

Apply physics-level imperfections in place on the **measured** ring's current slot, **before** `_apply_transform`. Default: no-op. Override when the simulator does not model a random fluctuation of the underlying phenomenon (genuine drift of the physical quantity, fine-scale turbulence on top of the deterministic field, etc.) and that fluctuation should propagate through the sensor's response model on subsequent steps. Measured-only by construction so GT keeps the raw simulated phenomenon - if you want the noise on both branches, write it into the simulator state instead.

This hook is **called from inside the default `_update_current_timestep_data`**, immediately after the raw signal is mirrored into the measured slot. A sensor that needs `_update_raw_data` and `_apply_physics_imperfections` fused in a single kernel pass should override `_update_current_timestep_data` instead of this hook (see [Kernel-internal physics noise](#kernel-internal-physics-noise) below). Anything that belongs to the sensor's readout electronics (noise, ADC quantization) belongs in `_apply_hardware_imperfections`; anything that belongs to the sensor element (RC time constant, mechanical bandwidth) belongs in `_apply_transform` with the `is_measured=True` gate.

#### `_apply_hardware_imperfections(cls, shared_metadata, measured_slot_0)`

`SimpleSensor` already implements an opinionated interpretation of `noise`, `bias`, `random_walk`, and `resolution` as the perturbations the embedded sampler introduces at the sensor output. Applied to the per-step measured working buffer **before** `_post_process` (and before the post-`_post_process` snapshot is frozen into the per-class return-space ring); the timeline ring is never written to, so `_apply_transform` recurrence stays clean. This is the **measured-only** stage of the pipeline; nothing here is mirrored on the GT branch.

Designed for stateless per-step perturbations. Stateful sensor-element effects (RC time constant, mechanical bandwidth) belong in `_apply_transform` with the `is_measured` gate (intermediate-space recurrence). Stateful post-acquisition DSP (anti-alias, decimation memory) belongs in `_post_process`, which sees the per-class return-space ring and can read its previous slots via `timeline.at(0)` and earlier (the return ring rotates after `_post_process` returns).

Override when your sensor has a non-standard imperfection model. You typically still call `super()._apply_hardware_imperfections(...)` for the standard pieces and add your custom term on top:

```python
@classmethod
def _apply_hardware_imperfections(cls, shared_metadata, measured_slot_0):
    # Standard contributions (noise, bias, random_walk, resolution).
    super()._apply_hardware_imperfections(shared_metadata, measured_slot_0)
    # Custom: signal-dependent noise sampled fresh each step (multiplicative noise floor).
    measured_slot_0 += torch.normal(0.0, shared_metadata.signal_noise_coeff) * measured_slot_0.abs()
```

#### `_update_current_timestep_data(cls, shared_metadata, current_ground_truth_data_T, ground_truth_data_timeline, measured_data_timeline)`

Default behavior: call `_update_raw_data` to produce the ground-truth value into the contiguous `(cols, B)` kernel target `current_ground_truth_data_T`, mirror it into the GT ring's slot 0 and the measured ring's slot 0, then call `_apply_physics_imperfections` in place on the measured slot. Override this method to fuse `_update_raw_data` and `_apply_physics_imperfections` in a single kernel pass: write the raw GT to `current_ground_truth_data_T` and to the GT ring slot, and write the noised value directly to the measured ring slot. The rest of the pipeline (`_apply_transform`, hardware imperfections, `_post_process`, delay sampling) still runs unchanged on top. See [Kernel-internal physics noise](#kernel-internal-physics-noise) below.

#### `uses_ring_pipeline` (class attribute, `ClassVar[bool]`)

Class-level capability flag declaring whether the class participates in the ring-based per-step pipeline inside `_update_shared_cache`. The default is `True`, which is what `Sensor` exposes and `SimpleSensor` inherits unchanged: every sensor that uses the standard orchestrator needs the GT and measured timeline rings. Subclasses whose `_update_shared_cache` bypasses the rings entirely (built-in cameras handle rendering lazily on read and never touch either timeline) set this to `False` so the manager skips the paired allocation.

Set it on the class itself, not on the instance - the manager reads it once at scene-build time to decide ring allocation per sensor class. Changing it after build has no effect because allocation is already done.

```python
class MyCustomSensor(Sensor[MyOptions, MyMetadata]):
    uses_ring_pipeline: ClassVar[bool] = False  # only if you implement `_update_shared_cache` from scratch
```

The runtime gating of imperfection contributions (`has_any_noise`, `has_any_bias`, etc.) is a separate concern handled inside `_apply_hardware_imperfections`; those flags are updated by the `set_*` setters and decide per-step which contributions cost any work. Ring allocation is binary: either the class uses the rings or it doesn't.

## Kernel-internal physics noise

Some sensors have noise that is **intrinsic to the physics computation** - a single kernel pass must produce both the ground-truth value (the ideal signal) and the noised measured value, because the noise is sampled inside the kernel and modulates intermediate quantities (e.g. a probe-radius perturbation that affects which face the ray hits). Splitting compute into "GT first, then add noise" is impossible: the noise is not a post-hoc addition, it shapes the kernel's branches.

Two supported routes:

1. **Override `_update_current_timestep_data` on `SimpleSensor`.** Your kernel writes `current_ground_truth_data_T` (the contiguous `(cols, B)` GT slice) **and** `measured_data_timeline.at(0, copy=False)` (the measured slot 0, `(B, cols)`) in one pass, and (when allocated) `ground_truth_data_timeline.at(0, copy=False)` (the GT slot 0). Because `_apply_physics_imperfections` is packed inside this hook, your override naturally fuses raw + physical-response noise. The rest of the SimpleSensor pipeline (`_apply_transform` on both branches, delay sampling, `_apply_hardware_imperfections`, eager `_post_process`) still runs on top. Recommended when you also want any of the standard pipeline pieces (imperfection parameters, delay/jitter, `_post_process` projection).
2. **Derive from `Sensor` directly and override `_update_shared_cache`.** Skips the SimpleSensor chain entirely. The override receives `(metadata, gt_T, gt_timeline, measured_timeline, intermediate_cache)` and is responsible for populating them. The manager handles `_post_process` projection, return-space ring writes, and delay sampling after the hook returns. Use this when the sensor needs a fundamentally non-standard pipeline (e.g. cameras and renderers).

## Camera-style sensors via `BaseCameraSensor`

`BaseCameraSensor` is a `Sensor`-direct subclass that codifies the lazy-render-on-read pattern shared by every Genesis camera (`RasterizerCameraSensor`, `RaytracerCameraSensor`, `BatchRendererCameraSensor`). Use it as the base for any custom sensor that produces an image by rendering the scene rather than by reading physics-time signals each step.

**Advantages over deriving from `Sensor` directly**

- Lazy render-on-read with per-step caching: multiple `read()` calls in the same simulation step share a single render. No need to implement `_update_shared_cache`.
- Link attachment with `pos`/`lookat`/`up` (or an explicit `offset_T`): the camera follows a `RigidLink` each frame and hands you the world-space transform to apply to your renderer.
- An RGB output of shape `((h, w, 3),)` and dtype `torch.uint8` declared from `options.res`, plus a `read(envs_idx=...) -> CameraData` returning a `NamedTuple(rgb=...)` (with the leading batch dim dropped when `n_envs == 0`).
- The class is opted out of the ring pipeline (`uses_ring_pipeline = False`), and `__init__` rejects `delay > 0`, `jitter > 0`, and `history_length > 0` so users cannot silently request features that this sensor type cannot honor.

**What you must implement**

Two hooks:

```python
class MyCameraSensor(BaseCameraSensor[MyCameraOptions]):
    def _apply_camera_transform(self, camera_T: torch.Tensor) -> None:
        # `camera_T` is a (4, 4) world-space transform. Apply it to your renderer's camera representation.
        ...

    def _render_current_state(self) -> None:
        # Render the scene from the current pose into the per-sensor slot of the per-class image cache.
        # Called at most once per simulation step per camera.
        ...
```

See `RasterizerCameraSensor` for a complete worked example.

**Limitations**

- Return is fixed to `((h, w, 3),)` `torch.uint8`. For depth, segmentation, normals, or any non-RGB output, override `_get_return_format` / `_get_cache_dtype` (and adapt the cache backing store), or drop down to a bare `Sensor` subclass.
- The standard `SimpleSensor` imperfection knobs (`noise`, `bias`, `random_walk`, `resolution`) are not available. Any sensor-imperfection model has to live inside `_render_current_state` or in a `_post_process` override.
- `history_length > 0` is rejected. Multi-frame stacks must be assembled by the caller across successive `read()` calls.

## Per-class metadata: what goes in `<Name>SharedMetadata`

Anything that is **per-sensor-class** (not per-instance) and is read by your hooks. Examples:

- Solver/entity references (one per scene).
- Per-sensor index tensors (`links_idx`, `expanded_links_idx`, `thresholds`, `min_force`, `max_force`, ...) - concatenated at build time, indexed inside the hooks.
- Per-sensor offsets (position, quaternion).
- Filter coefficients, IIR state, accumulators.
- Any per-class precomputed flags (`has_filter`, `has_any_jitter`, ...) that gate slow paths.

`SimpleSensorMetadata` provides the imperfection state out of the box (`noise`, `bias`, `random_walk`, `resolution`, `jitter_ts`, plus the matching `has_any_*` flags). Subclass it and add your fields with `make_tensor_field((shape,))` so they are auto-allocated:

```python
from dataclasses import dataclass
from genesis.engine.sensors.base_sensor import SimpleSensorMetadata
from genesis.utils.misc import make_tensor_field

@dataclass
class MySharedMetadata(RigidSensorMetadataMixin, SimpleSensorMetadata):
    thresholds: torch.Tensor = make_tensor_field((0,))
    custom_offsets: torch.Tensor = make_tensor_field((0, 3))
```

In your sensor's `build()`, append the per-sensor entries with `concat_with_tensor`. The manager calls `build()` once per sensor instance at scene-build time.

## Returning a NamedTuple instead of a tensor

For multi-tensor returns (IMU style), define a `NamedTuple` and parameterize the sensor class:

```python
class IMUData(NamedTuple):
    lin_acc: torch.Tensor
    ang_vel: torch.Tensor
    mag: torch.Tensor

class IMUSensor(SimpleSensor[IMU, IMUSharedMetadata, IMUData]):
    def _get_return_format(self) -> tuple[tuple[int, ...], ...]:
        # Shapes must match the NamedTuple field order.
        return ((3,), (3,), (3,))

    @classmethod
    def _get_cache_dtype(cls) -> torch.dtype:
        # Single dtype across all fields (class-uniform).
        return gs.tc_float
```

The manager allocates a single contiguous slab of `sum(shape_i)` scalars per sensor and slices it on read; the public `read()` reconstructs and returns the NamedTuple.

## Worked example - a minimal proximity sensor

```python
# my_plugin/options.py
from genesis.options.sensors.options import SimpleSensorOptions
from genesis.options.sensors.options import RigidSensorOptionsMixin

class MyProximity(
    RigidSensorOptionsMixin["MyProximitySensor"],
    SimpleSensorOptions["MyProximitySensor"],
):
    max_range: float = 1.0


# my_plugin/sensor.py
from dataclasses import dataclass

import torch

import genesis as gs
from genesis.engine.sensors.base_sensor import (
    SimpleSensor, SimpleSensorMetadata,
)
from genesis.engine.sensors.base_sensor import (
    RigidSensorMetadataMixin, RigidSensorMixin,
)
from genesis.utils.misc import concat_with_tensor, make_tensor_field

from .options import MyProximity


@dataclass
class MyProximityMetadata(RigidSensorMetadataMixin, SimpleSensorMetadata):
    max_range: torch.Tensor = make_tensor_field((0,))


class MyProximitySensor(
    RigidSensorMixin[MyProximityMetadata],
    SimpleSensor[MyProximity, MyProximityMetadata],
):
    def build(self):
        super().build()
        self._shared_metadata.max_range = concat_with_tensor(
            self._shared_metadata.max_range,
            float(self._options.max_range),
            expand=(1,),
        )

    def _get_return_format(self) -> tuple[int, ...]:
        return (1,)

    @classmethod
    def _get_cache_dtype(cls) -> torch.dtype:
        return gs.tc_float

    @classmethod
    def _update_raw_data(cls, shared_metadata, raw_data_T):
        pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)   # (B, N, 3)
        dist = pos.norm(dim=-1).clamp(max=shared_metadata.max_range)            # (B, N)
        raw_data_T.copy_(dist.T)                                                # (N, B)
```

That is enough for the sensor to be usable via `scene.add_sensor(MyProximity(entity_idx=0, ...))`. All of the imperfection plumbing (noise, bias, random walk, delay, jitter, history) is inherited from `SimpleSensor` and applied uniformly.

## Canonical examples: what built-in sensors override

To pick the right hook for your case, mirror the closest built-in sensor:

Every concrete sensor must implement `_get_return_format` (instance) and `_get_cache_dtype` (classmethod). The table below shows which additional hooks are overridden:

| Built-in sensor | `_update_raw_data` | `_update_current_timestep_data` | `_apply_transform` | `_post_process` + intermediate override |
|---|---|---|---|---|
| `ContactSensor` | yes (float kernel) | - | - | bool threshold (`tensor > metadata.thresholds`); return: `(1,)` bool, intermediate: `(1,)` float (via `_get_intermediate_dtype = gs.tc_float`). |
| `ContactForceSensor` | yes | - | - | stateless clamp + deadband; shape/dtype preserved; no-op `_get_intermediate_dtype` override as explicit acknowledgement. |
| `IMUSensor` | yes | - | yes (body-frame rotation; no filter) | identity |
| `ProximitySensor` | yes | - | - | identity |
| `RaycasterSensor` / `DepthCameraSensor` | yes | - | - | identity |
| `TemperatureGridSensor` | yes (raw temperature kernel) | - | yes (RC filter that reads `timeline.at(1)` on both branches; recurrence stays clean because hardware imperfections never reach the ring) | identity |
| `ElastomerDisplacementSensor` | yes | - | - | identity |
| Camera (any `*CameraSensor`) | - | - | - | identity. Derives from `BaseCameraSensor`; see [Camera-style sensors via BaseCameraSensor](#camera-style-sensors-via-basecamerasensor). |

`_apply_hardware_imperfections` is **inherited unchanged** by every `SimpleSensor`-derived sensor - the out-of-the-box implementation already handles `noise + bias + random_walk + resolution`. Override only when your sensor needs a non-standard imperfection model.

## Things to double-check

- **Populate `raw_data_T` in place; do not rebind it.** It is the implementer's responsibility: assigning `raw_data_T = something_new` inside the override leaves the framework-owned buffer untouched and silently breaks the pipeline. Write via `raw_data_T.copy_(...)`, `raw_data_T[...] = ...`, or a kernel that takes `raw_data_T` as its output argument.
- **Reads are idempotent.** Do not put state mutation inside `read()`. Mutation belongs in the per-step hooks which the manager calls once per simulation step.
- **Hooks are called once per class, not per instance or per env.** Vectorize accordingly.
- **Shape is per-instance; dtype is class-uniform.** `_get_return_format` / `_get_intermediate_format` are instance methods so options can affect the shape; `_get_cache_dtype` / `_get_intermediate_dtype` are classmethods because every instance of a class must share one dtype.
- **Overriding `_post_process` requires overriding `_get_intermediate_format` and/or `_get_intermediate_dtype`.** Even a no-op override is acceptable when shape and dtype both coincide with the return space - it is the explicit acknowledgement that the intermediate buffer is distinct.
- **Recommended utilities.** `concat_with_tensor`, `make_tensor_field`, and `tensor_to_array` from `genesis.utils.misc` match the conventions used by every built-in sensor; reusing them keeps your sensor consistent with the rest of the codebase.
