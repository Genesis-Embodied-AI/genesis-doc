# 🔧 Implementing Custom Sensors

This page is a guide for advanced users who want to add their own sensor type. It is the writer's counterpart to [Sensor Pipeline](sensor_pipeline.md), which describes how the pipeline executes at runtime; here we focus on which hooks to override, what shape/dtype contracts they must satisfy, and how the automatic plugin registration works.

In almost every case, derive from `SimpleSensor` and override **only the hooks you need**. Deriving directly from `Sensor` is reserved for sensors that bypass the standard pipeline entirely (the built-in cameras do this).

## What you write to add a sensor

To add a new sensor you contribute four artifacts:

| Artifact | Where | Role |
|---|---|---|
| `<Name>` (an options class) | `genesis/options/sensors/<name>.py` (or your plugin package) | Public, user-facing dataclass that carries every per-sensor parameter. Inherits `SimpleSensorOptions` (or the appropriate mixin). Generic-parameterized with the sensor class as a forward reference. |
| `<Name>SharedMetadata` | next to the sensor implementation | Per-sensor-class runtime state shared across every instance of this sensor in the scene. Inherits `SimpleSensorMetadata` (or `SharedSensorMetadata` for non-Simple sensors). |
| `<Name>Sensor` | next to the sensor implementation | The sensor class itself. Inherits `SimpleSensor[<Name>, <Name>SharedMetadata]` and overrides `_get_return_format` (instance, shape), `_get_cache_dtype` (classmethod, dtype), `_update_raw_data`, plus optionally `_apply_transform`, `_post_process` (paired with `_get_intermediate_format` and/or `_get_intermediate_dtype`). |
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
| `SimpleSensor[OptionsT, MetadataT]` | Almost always. Per-step pipeline (raw data -> transform/filter -> hardware imperfections -> delay -> post-process). |
| `SimpleSensor[OptionsT, MetadataT, DataT]` | Same as above, but `read()` returns an instance of `DataT` (a `NamedTuple`) instead of a single tensor. IMU is the canonical example. |
| `Sensor[OptionsT, MetadataT]` | Only when the standard pipeline does not apply. The built-in cameras derive from `Sensor` directly because they own their rendering path. Overriding at this level means implementing `_update_shared_cache` yourself, and (if your implementation does not use the measured ring) setting the class attribute `uses_measured_pipeline = False` to skip ring allocation. Also the right choice when you want **full kernel control** and need a single kernel pass to write both the ground-truth slice and the measured-timeline slot with internal noise (see [Kernel-internal physics noise](#kernel-internal-physics-noise) below). |

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

Classmethod returning the **dtype** of what `read()` returns. Dtype is class-uniform: a single dtype shared by every instance of the sensor class. This is a load-bearing invariant of the manager — the per-class slice into the per-dtype intermediate buffer must be contiguous, so all instances of a class must share one dtype. If you need different dtypes for different instances, use two different sensor classes.

```python
@classmethod
def _get_cache_dtype(cls) -> torch.dtype:
    return gs.tc_float
```

The split between an instance method for shape and a classmethod for dtype is deliberate: it lets the manager resolve the per-class dtype without instantiating any sensor, while still allowing the per-instance shape to depend on options.

#### `_update_raw_data(cls, shared_metadata, raw_data_T)`

The sensor-specific kernel that computes the **ground-truth** value of every sensor of this class for the current timestep. The output buffer `raw_data_T` has shape `(cols, B)` — **column-major**, batch dimension last — to be C-contiguous for per-class row slices when other sensors write to the same intermediate cache. Always populate the buffer in place.

```python
@classmethod
def _update_raw_data(cls, shared_metadata, raw_data_T):
    pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)   # (B, N, 3)
    raw_data_T.copy_(pos.reshape(pos.shape[0], -1).T)                       # (3*N, B)
```

This is the only abstract hook of `SimpleSensor`. `_get_return_format` and `_get_cache_dtype` from the base `Sensor` are also required (see above). Everything else has a sensible default.

### Optional overrides

#### `_apply_transform(cls, shared_metadata, data, *, timeline=None)`

Apply a coordinate transform and/or a stateful temporal filter, in place, on `data` (a batch-first view `[B, cache_size, ...]`). Called twice per step: once on the ground-truth branch (`timeline=None`) and once on the measured branch (`timeline=<measured ring>`). The GT branch deliberately cannot run a filter - ground truth is the ideal signal with no hardware response.

- The coordinate-transform portion should be unconditional (executed on both branches).
- The filter portion (e.g. exponential moving average, low-pass) must be gated on `if timeline is not None:` and read previous slots via `timeline.at(1)`, `timeline.at(2)`, etc. Filter-then-transform is not expressible by design - within a single override, write transform code first, then filter code.
- **Aliasing note:** on the measured branch, `data is timeline.at(0, copy=False)` - they refer to the same memory. Use whichever reads more naturally and do not double-write.

```python
@classmethod
def _apply_transform(cls, shared_metadata, data, *, timeline=None):
    # transform branch: always runs
    data.copy_(transform_by_quat(data, shared_metadata.world_to_local_quat))

    # filter branch: measured only
    if timeline is not None and shared_metadata.has_filter:
        prev = timeline.at(1)
        data.mul_(1 - shared_metadata.alpha).add_(prev, alpha=shared_metadata.alpha)
```

#### `_post_process(cls, shared_metadata, tensor) -> torch.Tensor`

Eager projection from intermediate space to return space. Override when the user-facing output type and/or shape differs from the pipeline-internal representation: bool threshold on `ContactSensor`, deadband + saturation on `ContactForceSensor`, etc. Returns a new tensor (the manager copies it into the return cache).

**Stateful is allowed.** Because the manager calls `_post_process` exactly once per simulation step, the override may carry per-call state in `metadata` (or in a dedicated cached attribute) and advance it on each call. This makes `_post_process` a natural home for software-level signal processing that the sensor offers on top of the raw measurement - complementary filter, Mahony filter, Kalman filter, an IMU quaternion estimator. Whether to put such estimators in the sensor's `_post_process` or in the user's controller is a design choice; both placements are valid. High-end IMUs that ship a fused orientation estimate are a real example of `_post_process`-shaped behavior.

```python
@classmethod
def _post_process(cls, shared_metadata, tensor):
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

Instance method returning the shape of the **pipeline-internal** buffer (delay sampling, transform, filters, hardware imperfections all happen in this space). Defaults to `_get_return_format()`. Override together with `_post_process` whenever your projection changes shape, or as a no-op acknowledgement when only `_get_intermediate_dtype` would otherwise differ.

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

When `_get_intermediate_format` and `_get_intermediate_dtype` both default (and `_post_process` is identity, the common case), the manager allocates **one** buffer and aliases the return cache as a view of the intermediate cache. No extra memory, no copy.

#### `_apply_hardware_imperfections(cls, shared_metadata, measured_slot_0)`

`SimpleSensor` already implements an opinionated interpretation of `noise`, `bias`, `random_walk`, and `resolution` as the perturbations the embedded sampler introduces at snapshot time. Override only when your sensor has a non-standard imperfection model - e.g. when noise must be added in a non-Cartesian space, or when the hardware-specific noise model is coupled to the raw signal in a way the generic implementation cannot express. In that case, you typically still call `super()._apply_hardware_imperfections(...)` for the standard pieces and add your custom term on top.

#### `_update_current_timestep_data(cls, shared_metadata, current_ground_truth_data_T, measured_data_timeline)`

Default behavior: call `_update_raw_data` to produce the ground-truth value, then copy it into the measured ring's current slot. Override **only** when your sensor has **kernel-internal physical-response noise**, i.e. when the ground-truth signal and the measured signal must be produced by a single kernel pass with different paths inside. The default split (one kernel, then copy) is correct for every other case. See [Kernel-internal physics noise](#kernel-internal-physics-noise) below.

#### `uses_measured_pipeline` (class attribute, `ClassVar[bool]`)

Class-level capability flag declaring whether the class reads or writes the measured-timeline ring inside `_update_shared_cache`. The default is `True`, which is what `Sensor` exposes and `SimpleSensor` inherits unchanged: every sensor that uses the standard orchestrator needs the ring. Subclasses whose `_update_shared_cache` bypasses the ring entirely (built-in cameras handle rendering lazily on read and never touch `measured_data_timeline`) set this to `False` so the manager skips the allocation.

Set it on the class itself, not on the instance - the manager reads it once at scene-build time to decide ring allocation per sensor class. Changing it after build has no effect because allocation is already done.

```python
class MyCustomSensor(Sensor[MyOptions, MyMetadata]):
    uses_measured_pipeline: ClassVar[bool] = False  # only if you implement `_update_shared_cache` from scratch
```

The runtime gating of imperfection contributions (`has_any_noise`, `has_any_bias`, etc.) is a separate concern handled inside `_apply_hardware_imperfections`; those flags are updated by the `set_*` setters and decide per-step which contributions cost any work. Ring allocation is binary: either the class uses the ring or it doesn't.

## Kernel-internal physics noise

Some sensors have noise that is **intrinsic to the physics computation** - a single kernel pass must produce both the ground-truth value (the ideal signal) and the noised measured value, because the noise is sampled inside the kernel and modulates intermediate quantities (e.g. a probe-radius perturbation that affects which face the ray hits). Splitting compute into "GT first, then add noise" is impossible: the noise is not a post-hoc addition, it shapes the kernel's branches.

Two supported routes:

1. **Override `_update_current_timestep_data` on `SimpleSensor`.** Your kernel writes `current_ground_truth_data_T` (the GT slice, `(cols, B)`) **and** `measured_data_timeline.at(0, copy=False)` (the measured slot 0, `(B, cols)`) in one pass. The rest of the SimpleSensor pipeline (`_apply_transform` on both branches, `_apply_hardware_imperfections`, delay sampling, eager `_post_process`) still runs on top. Recommended when you also want any of the standard pipeline pieces (imperfection parameters, delay/jitter, `_post_process` projection).
2. **Derive from `Sensor` directly and override `_update_shared_cache`.** Skips the SimpleSensor chain entirely.
   The override receives `(metadata, gt_T, measured_timeline, intermediate_cache, return_cache)` and is
   responsible for populating them. Use this when the sensor needs a fundamentally non-standard pipeline (e.g.
   cameras and renderers).

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
| `TemperatureGridSensor` | yes (raw temperature kernel) | - | yes (RC filter; `if timeline is not None: data.copy_(alpha * data + (1 - alpha) * timeline.at(1))`) | identity |
| `ElastomerDisplacementSensor` | yes | - | - | identity |
| Camera (any `*CameraSensor`) | - | - | - | identity. Derives from `Sensor` directly; owns `_update_shared_cache`; `uses_measured_pipeline = False`. |

`_apply_hardware_imperfections` is **inherited unchanged** by every `SimpleSensor`-derived sensor - the out-of-the-box implementation already handles `noise + bias + random_walk + resolution`. Override only when your sensor needs a non-standard imperfection model.

## Things to double-check

- **Populate `raw_data_T` in place; do not rebind it.** It is the implementer's responsibility: assigning `raw_data_T = something_new` inside the override leaves the framework-owned buffer untouched and silently breaks the pipeline. Write via `raw_data_T.copy_(...)`, `raw_data_T[...] = ...`, or a kernel that takes `raw_data_T` as its output argument.
- **Reads are idempotent.** Do not put state mutation inside `read()`. Mutation belongs in the per-step hooks which the manager calls once per simulation step.
- **Hooks are called once per class, not per instance or per env.** Vectorize accordingly.
- **Shape is per-instance; dtype is class-uniform.** `_get_return_format` / `_get_intermediate_format` are instance methods so options can affect the shape; `_get_cache_dtype` / `_get_intermediate_dtype` are classmethods because every instance of a class must share one dtype.
- **Overriding `_post_process` requires overriding `_get_intermediate_format` and/or `_get_intermediate_dtype`.** Even a no-op override is acceptable when shape and dtype both coincide with the return space - it is the explicit acknowledgement that the intermediate buffer is distinct.
- **Recommended utilities.** `concat_with_tensor`, `make_tensor_field`, and `tensor_to_array` from `genesis.utils.misc` match the conventions used by every built-in sensor; reusing them keeps your sensor consistent with the rest of the codebase.
