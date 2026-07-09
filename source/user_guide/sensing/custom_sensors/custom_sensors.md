# Writing a custom sensor

This page is for advanced users adding a new sensor type. It is the author's counterpart to the {doc}`sensor pipeline <sensor_pipeline>`, which describes how sensors execute at runtime; here the focus is the interface you implement, the shape and dtype contracts each override must honor, and how the framework pairs your sensor with its options automatically. If you only want to *use* the built-in sensors, start with {doc}`/user_guide/sensing/index` instead.

The base classes live in `genesis/engine/sensors/base_sensor.py`. In almost every case you derive from `SimpleSensor` and override only the hooks you need. Deriving directly from `Sensor` is reserved for sensors that bypass the standard pipeline entirely, and the built-in cameras do exactly that through `BaseCameraSensor`.

## Minimal working example

A complete sensor is three classes: a user-facing options dataclass, a per-class metadata container, and the sensor itself. The following proximity sensor reports the distance from an attached link to the world origin, clamped to a maximum range. It is enough to be usable through `scene.add_sensor(...)`, and every imperfection feature (noise, bias, random walk, delay, jitter, history) is inherited from `SimpleSensor` and applied uniformly.

```python
# my_plugin/options.py
from genesis.options.sensors.options import RigidSensorOptionsMixin, SimpleSensorOptions


class MyProximity(
    RigidSensorOptionsMixin["MyProximitySensor"],
    SimpleSensorOptions["MyProximitySensor"],
):
    max_range: float = 1.0  # meters
```

```python
# my_plugin/sensor.py
from dataclasses import dataclass

import torch

import genesis as gs
from genesis.engine.sensors.base_sensor import (
    RigidSensorMetadataMixin,
    RigidSensorMixin,
    SimpleSensor,
    SimpleSensorMetadata,
)
from genesis.utils.misc import concat_with_tensor, make_tensor_field

from .options import MyProximity


@dataclass
class MyProximityMetadata(RigidSensorMetadataMixin, SimpleSensorMetadata):
    # Per-sensor ranges, concatenated across every instance of this class at build time.
    max_range: torch.Tensor = make_tensor_field((0,))


class MyProximitySensor(
    RigidSensorMixin[MyProximityMetadata],
    SimpleSensor[MyProximity, None, MyProximityMetadata],
):
    def build(self):
        # The manager calls build() once per instance. Append this sensor's parameters
        # to the shared, per-class tensors so one kernel can run over every instance.
        super().build()
        self._shared_metadata.max_range = concat_with_tensor(
            self._shared_metadata.max_range,
            float(self._options.max_range),
            expand=(1,),
        )

    def _get_return_format(self) -> tuple[int, ...]:
        return (1,)  # one scalar per sensor

    @classmethod
    def _get_cache_dtype(cls) -> torch.dtype:
        return gs.tc_float

    @classmethod
    def _update_raw_data(cls, shared_context, shared_metadata, raw_data_T):
        pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)  # (B, N, 3)
        dist = pos.norm(dim=-1).clamp(max=shared_metadata.max_range)           # (B, N)
        raw_data_T.copy_(dist.T)  # write in place; buffer is (cols, B), column-major
```

The rest of this page explains why each piece exists and which additional hooks the more elaborate sensors override.

## The classes you write

Every sensor contributes the same three artifacts, plus two optional ones.

- **Options class:** a public dataclass carrying every per-sensor parameter, inheriting `SimpleSensorOptions` (or the appropriate mixin). It is generic-parameterized with the sensor class as a forward reference, `SimpleSensorOptions["MyProximitySensor"]`. This is the only object the user constructs.
- **Metadata class:** the per-sensor-*class* runtime state shared by every instance of the sensor in a scene. It inherits `SimpleSensorMetadata` for `SimpleSensor`-derived sensors, or `SharedSensorMetadata` for sensors deriving from `Sensor` directly.
- **Sensor class:** the implementation. It inherits `SimpleSensor[OptionsT, ContextT, MetadataT]` and overrides the hooks below.
- **A `NamedTuple` return type (optional):** declare one when the sensor returns several tensors, and pass it as the fourth type parameter. See [Returning a NamedTuple](#returning-a-namedtuple).
- **A `SharedSensorContext` subclass (optional):** declare one only when this sensor shares an expensive resource with *other* sensor types, and pass it as the second type parameter. See [Sharing a resource across sensor types](#sharing-a-resource-across-sensor-types).

The generic signature is `Sensor[OptionsT, ContextT, MetadataT, DataT]`: options first, then the cross-type shared context (`None` when there is none), then the metadata type, then the data type (`DataT` defaults to `tuple`).

## Registration is automatic

Sensors are never registered by hand. When a `Sensor` subclass names its options class as the first type parameter, `Sensor.__init_subclass__` records the pairing in `SensorManager.SENSOR_TYPES_MAP` the moment the class body runs. The user then only ever constructs the options instance and hands it to `scene.add_sensor(...)`, which resolves the sensor class, instantiates it, and returns the sensor.

That leaves two supported placements:

- **In-tree (built-in sensors):** options in `genesis/options/sensors/*.py`, sensor in `genesis/engine/sensors/*.py`. Both are imported through their package `__init__`, so the pairing is registered at import.
- **Out-of-tree (third-party plugins):** put your options and sensor in sibling submodules of one package (for example `my_plugin/options.py` and `my_plugin/sensor.py`). As long as your code imports the options module before constructing the options, the framework resolves the sensor class transparently on the first `scene.add_sensor(...)` call.

:::{note}
`__init_subclass__` also enforces the contract: a concrete sensor that declares its own options class must also declare its metadata type parameter, and any class that overrides `_post_process` must declare an intermediate buffer (see [Projecting to a different return type](#projecting-to-a-different-return-type)). Both violations raise `TypeError` at class-definition time, before any scene is built.
:::

## Required overrides

Two overrides are required of every concrete sensor, and `SimpleSensor` adds a third.

- **`_get_return_format(self) -> tuple[...]`:** an instance method returning the *shape* of what `read()` produces. Shape is per-instance by design, because options may legitimately determine it (a raycaster's pattern, a camera's resolution, a proximity sensor's probe positions). Return `(N,)` for a single tensor of `N` scalars, or a tuple of tuples such as `((3,), (3,), (3,))` for a multi-tensor return.
- **`_get_cache_dtype(cls) -> torch.dtype`:** a classmethod returning the dtype of what `read()` produces. Dtype is class-uniform, not per-instance: the manager packs every instance of a class into one contiguous per-class slice of a per-dtype buffer, so all instances must share one dtype. If you need different dtypes, use two sensor classes.
- **`_update_raw_data(cls, shared_context, shared_metadata, raw_data_T)`:** the `SimpleSensor` kernel that computes the *ground-truth* value for every sensor of this class at the current step. This is `SimpleSensor`'s single abstract producing hook.

The split between an instance method for shape and a classmethod for dtype is deliberate. It lets the manager resolve the per-class dtype without instantiating a sensor, while still letting the per-instance shape depend on options.

`raw_data_T` has shape `(cols, B)` (column-major, with the batch dimension `B` last) so that per-class row slices are C-contiguous when several sensor classes write into the same intermediate cache. Always populate it in place:

```python
@classmethod
def _update_raw_data(cls, shared_context, shared_metadata, raw_data_T):
    pos = shared_metadata.solver.get_links_pos(shared_metadata.links_idx)  # (B, N, 3)
    raw_data_T.copy_(pos.reshape(pos.shape[0], -1).T)                      # (3*N, B)
```

`shared_context` is the cross-type resource, or `None`; most sensors ignore it. Hooks are called once per class per step, never per instance and never per environment, so vectorize accordingly.

## Choosing a base class

| Base | When to use |
|---|---|
| `SimpleSensor[OptionsT, None, MetadataT]` | Almost always. The standard per-step pipeline: raw, physics imperfections, transform, hardware imperfections, post-process, delay sampling. |
| `SimpleSensor[OptionsT, None, MetadataT, DataT]` | Same pipeline, but `read()` returns an instance of `DataT`, a `NamedTuple`, instead of a single tensor. The IMU is the canonical example. |
| `BaseCameraSensor[OptionsT]` | Camera-style sensors that render an image lazily on `read()`. See [Camera-style sensors](#camera-style-sensors). |
| `Sensor[OptionsT, None, MetadataT]` | Only when neither standard pipeline fits. You then implement `_update_shared_cache` yourself, and set `uses_ring_pipeline = False` if your implementation never touches the timeline rings. |

Mixins compose onto the base:

- **`RigidSensorOptionsMixin` / `KinematicSensorOptionsMixin`:** on the options side, for sensors attached to a `RigidEntity` or any `KinematicEntity` respectively. Combine with `SimpleSensorOptions` through multiple inheritance.
- **`RigidSensorMixin` / `RigidSensorMetadataMixin`:** on the sensor and metadata side, giving you a typed `solver` field, the `links_idx` bookkeeping, and `set_pos_offset` / `set_quat_offset`.

## Per-class metadata

The metadata class holds anything that is per-sensor-class rather than per-instance and is read by your hooks: solver and entity references, per-sensor index tensors concatenated at build time (`links_idx`, `thresholds`, `max_range`), per-sensor offsets, filter coefficients, and precomputed flags that gate slow paths.

`SimpleSensorMetadata` already provides the imperfection state (`noise`, `bias`, `random_walk`, `resolution`, `jitter_ts`) and the matching `has_any_*` flags. Subclass it and declare your fields with `make_tensor_field((shape,))` so they are auto-allocated:

```python
@dataclass
class MySharedMetadata(RigidSensorMetadataMixin, SimpleSensorMetadata):
    thresholds: torch.Tensor = make_tensor_field((0,))
    custom_offsets: torch.Tensor = make_tensor_field((0, 3))
```

In your sensor's `build()`, append this instance's entries with `concat_with_tensor`, as in the minimal example above. The manager calls `build()` once per sensor instance at scene-build time; growing the shared tensors there is what lets a single kernel run over every instance at once.

## Optional pipeline hooks

`SimpleSensor` runs a fixed per-step pipeline and gives every stage a default. Override a stage only when your sensor needs it. The stages run per branch, in this order:

- **Ground-truth branch:** `_update_raw_data`, then `_apply_transform(is_measured=False)`, then `_post_process(is_measured=False)`.
- **Measured branch:** `_update_raw_data`, then `_apply_physics_imperfections`, then `_apply_transform(is_measured=True)`, then `_apply_hardware_imperfections`, then `_post_process(is_measured=True)`, then delay sampling.

Both branches keep their own intermediate-space timeline ring holding post-transform, pre-hardware-imperfection values, so a stateful `_apply_transform` filter always reads previous slots that are clean of hardware noise. The distinction between the three noise stages is where the perturbation physically originates.

- **`_apply_physics_imperfections(cls, shared_metadata, data, timeline)`:** random fluctuation of the underlying phenomenon that the simulator does not model (genuine drift, fine-scale turbulence on the field). Measured-only, applied before `_apply_transform`, so it propagates through the response model on later steps. Default: no-op.
- **`_apply_transform(cls, shared_metadata, data, timeline, *, is_measured)`:** a coordinate transform and/or a stateful response model of the *sensor element* (thermal mass, RC time constant, mechanical bandwidth). Called on both branches; the coordinate part runs unconditionally, and you gate an element-specific effect that must not appear in ground truth on `if is_measured:`. Mutate `data` in place; read history with `timeline.at(1)`, `timeline.at(2)`. The IMU uses this for its body-frame alignment rotation; the temperature-grid sensor uses it for an RC filter.
- **`_apply_hardware_imperfections(cls, shared_metadata, measured_slot_0)`:** the perturbations the readout electronics introduce at the sensor output. `SimpleSensor` already implements `noise`, `bias`, `random_walk`, and `resolution` here, gated by the `has_any_*` flags so an all-zero class pays nothing. Override only for a non-standard model, and call `super()` first for the standard terms:

```python
@classmethod
def _apply_hardware_imperfections(cls, shared_metadata, measured_slot_0):
    super()._apply_hardware_imperfections(shared_metadata, measured_slot_0)
    # Signal-dependent noise floor, resampled each step.
    measured_slot_0 += torch.normal(0.0, shared_metadata.signal_noise_coeff) * measured_slot_0.abs()
```

For a sensor whose noise is intrinsic to the physics computation (a single kernel pass must produce both the ideal and the noised value because the noise shapes the kernel's branches), override `_update_current_timestep_data` instead. It writes the ground-truth slice and the noised measured slot in one pass, and the rest of the pipeline still runs on top.

### Projecting to a different return type

`_post_process(cls, shared_metadata, tensor, timeline, *, is_measured) -> torch.Tensor` projects from the pipeline-internal intermediate space into the user-facing return space. Override it when the output type or shape differs from the internal representation: a bool threshold on `ContactSensor`, a deadband and saturation on `ContactForceSensor`. Return the projected tensor; the manager writes it into the return-space ring and delay-samples it.

```python
@classmethod
def _post_process(cls, shared_metadata, tensor, timeline, *, is_measured):
    return tensor > shared_metadata.thresholds  # float intermediate, bool return
```

Overriding `_post_process` *requires* also overriding `_get_intermediate_format` and/or `_get_intermediate_dtype`; the framework raises `TypeError` at class-definition time otherwise. The reason is structural: the intermediate buffer must be a distinct buffer, because the timeline ring lives in intermediate space and mixing data spaces would corrupt any `_apply_transform` filter that reads previous slots. When the projection genuinely preserves shape and dtype, override one of them as a no-op returning the return-space value: the override is the explicit acknowledgment that the buffers are distinct.

- **`_get_intermediate_format(self)`:** shape of the internal buffer; defaults to `_get_return_format()`.
- **`_get_intermediate_dtype(cls)`:** dtype of the internal buffer; defaults to `_get_cache_dtype()`. `ContactSensor` overrides it to `gs.tc_float` because its kernel is float but its return is bool.

## Returning a NamedTuple

For a multi-tensor return, declare a `NamedTuple` and pass it as the fourth type parameter. `_get_return_format` then returns one shape per field, in field order:

```python
class IMUReturnType(NamedTuple):
    lin_acc: torch.Tensor
    ang_vel: torch.Tensor
    mag: torch.Tensor


class IMUSensor(SimpleSensor[IMU, None, IMUSharedMetadata, IMUReturnType]):
    def _get_return_format(self) -> tuple[tuple[int, ...], ...]:
        return ((3,), (3,), (3,))  # shapes match the NamedTuple field order

    @classmethod
    def _get_cache_dtype(cls) -> torch.dtype:
        return gs.tc_float  # one dtype across all fields (class-uniform)
```

The manager allocates a single contiguous slab per sensor and slices it on read; `read()` reconstructs and returns the `NamedTuple`, with the leading batch dimension dropped when the scene has no environments. Each field has shape `([n_envs,] *field_shape)`.

## Sharing a resource across sensor types

Metadata and a shared context are both manager-held state, but they solve different problems and must not be conflated. Metadata is *per-type*: it aggregates the per-sensor rows of one class so a single kernel can vectorize over them, and it grows with the number of sensors. A context is *cross-type*: a single resource, `O(1)` in the number of sensors, that several sensor classes read.

The canonical context is the collision BVH that both `RaycasterSensor` and `DepthCameraSensor` cast against. Building it once and letting both read it avoids rebuilding identical trees per type. A context is purely an optimization: results must be identical whether or not it is shared, so cross-sensor consistency stays the manager's responsibility.

`SharedSensorContext` is an abstract base built around `activate` / `is_active`; a subclass must implement every lifecycle method. Reading the resource before activation must raise, and `update` / `reset` must no-op while inactive:

```python
from genesis.engine.sensors.base_sensor import SharedSensorContext


class MyBVHContext(SharedSensorContext):
    def __init__(self, sim):
        super().__init__(sim)  # stores the sim, marks the context inactive
        self._bvh = None

    @property
    def bvh(self):
        if not self.is_active:
            raise gs.GenesisException("MyBVHContext queried before activation.")
        return self._bvh

    def activate(self):  # idempotent; the first consumer's build() triggers construction
        if self.is_active:
            return
        self._active = True
        self._bvh = build_bvh(self._sim)

    def update(self):  # once per step, before any consuming sensor reads it
        if self.is_active:
            self._bvh.refresh()

    def reset(self, envs_idx):  # on scene.reset()
        if self.is_active:
            self._bvh.flag_rebuild()

    def destroy(self):  # on teardown
        self._bvh = None
```

Declare it as the second `Sensor[...]` type parameter, activate it from `build()`, and read it through the leading `shared_context` argument of the producing hooks:

```python
class MySensor(SimpleSensor[MyOptions, MyBVHContext, MySharedMetadata]):
    def build(self):
        super().build()
        self._shared_context.activate()  # idempotent; the first consumer builds the resource

    @classmethod
    def _update_raw_data(cls, shared_context, shared_metadata, raw_data_T):
        raw_data_T.copy_(query(shared_context.bvh, ...))
```

Two sensor types that declare the same context class share one instance. The manager refreshes every active context once per step before the per-type update loop, so a context read inside `_update_raw_data` is already current. A sensor type that declares `None` receives `shared_context=None`.

## Camera-style sensors

`BaseCameraSensor` is a `Sensor`-direct subclass that codifies the lazy-render-on-read pattern of every built-in camera (`RasterizerCameraSensor`, `RaytracerCameraSensor`, `BatchRendererCameraSensor`). Use it for any sensor that produces an image by rendering the scene rather than by reading physics signals each step. It gives you:

- **Lazy render-on-read with per-step caching:** multiple `read()` calls in one step share a single render, so you never implement `_update_shared_cache`.
- **Link attachment** with `pos` / `lookat` / `up`, handing you the world-space transform to apply to your renderer each frame.
- **An RGB output** of shape `([n_envs,] h, w, 3)` and dtype `torch.uint8`, declared from `options.res`, returned as a `CameraReturnType` `NamedTuple`.

It opts out of the ring pipeline (`uses_ring_pipeline = False`) and rejects `delay`, `jitter`, and `history_length` at construction, since those depend on the return-space ring it does not allocate. You implement two hooks:

```python
class MyCameraSensor(BaseCameraSensor[MyCameraOptions]):
    def _apply_camera_transform(self, camera_T: torch.Tensor) -> None:
        # camera_T is a (4, 4) world-space transform. Apply it to your renderer's camera.
        ...

    def _render_current_state(self) -> None:
        # Render into this camera's slot of the per-class image cache. At most once per step.
        ...
```

See `RasterizerCameraSensor` for a complete worked example. The standard imperfection knobs are unavailable here; any imperfection model must live inside `_render_current_state` or a `_post_process` override. For non-RGB output (depth, segmentation, normals), override `_get_return_format` / `_get_cache_dtype` and adapt the backing store, or drop down to a bare `Sensor` subclass.

## What the built-in sensors override

To pick the right hooks, mirror the closest built-in sensor. Every one implements `_get_return_format` and `_get_cache_dtype`; the table shows the additional overrides.

| Sensor | `_update_raw_data` | `_apply_transform` | `_post_process` (+ intermediate) |
|---|---|---|---|
| `JointTorqueSensor` | yes | — | identity; return `(n_dofs,)` float |
| `ContactSensor` | yes | — | bool threshold; return `(1,)` bool, intermediate `(1,)` float via `_get_intermediate_dtype` |
| `ContactForceSensor` | yes | — | clamp and deadband; shape and dtype preserved, no-op intermediate override as acknowledgment |
| `IMUSensor` | yes | yes (body-frame alignment) | identity; `NamedTuple` return |
| `RaycasterSensor` / `DepthCameraSensor` | yes | — | identity |
| `TemperatureGridSensor` | yes | yes (RC filter reading `timeline.at(1)`) | identity |
| Any `*CameraSensor` | — | — | identity; derives from `BaseCameraSensor` |

`_apply_hardware_imperfections` is inherited unchanged by every `SimpleSensor`; override it only for a non-standard imperfection model.

## Things to double-check

- **Populate `raw_data_T` in place; never rebind it.** Assigning `raw_data_T = something_new` leaves the framework-owned buffer untouched and silently breaks the pipeline. Write via `raw_data_T.copy_(...)`, `raw_data_T[...] = ...`, or a kernel that takes it as an output argument.
- **Reads are idempotent.** Do not mutate state inside `read()`. State changes belong in the per-step hooks the manager calls once per step.
- **Hooks run once per class, not per instance or per environment.** Vectorize over the concatenated per-class tensors.
- **Shape is per-instance; dtype is class-uniform.** `_get_return_format` and `_get_intermediate_format` are instance methods so options can affect shape; `_get_cache_dtype` and `_get_intermediate_dtype` are classmethods because every instance shares one dtype.
- **Reuse the codebase utilities.** `concat_with_tensor`, `make_tensor_field`, and `tensor_to_array` from `genesis.utils.misc` match the conventions every built-in sensor follows.

## See also

- {doc}`sensor_pipeline`: how the pipeline executes at runtime, and the intermediate-versus-return separation in full.
- {doc}`/user_guide/sensing/index`: using the built-in sensors.
