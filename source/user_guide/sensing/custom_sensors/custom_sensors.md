# Writing a custom sensor

This page is for advanced users adding a new sensor type. It is the author's counterpart to the {doc}`sensor pipeline <sensor_pipeline>`, which describes how sensors execute at runtime; here the focus is the interface you implement, the shape and dtype contracts each override must honor, and how the framework pairs your sensor with its options automatically. If you only want to *use* the built-in sensors, start with {doc}`/user_guide/sensing/index` instead.

The base classes live in `genesis/engine/sensors/base_sensor.py`. In almost every case, derive your array from `SimpleSensorArray` and your handle from `SimpleSensor`, and override only the hooks you need. Derive directly from `SensorArray` only for a sensor that bypasses the standard pipeline entirely, as the built-in cameras do through `CameraSensorArray`.

## Minimal working example

A complete sensor is three classes: a user-facing options dataclass, an *array* holding the tensors of every sensor of the type and running the per-step computation over all of them at once, and the *handle* the user receives from `scene.add_sensor(...)`. The following proximity sensor reports the distance from an attached link to the world origin, clamped to a maximum range. It is enough to be usable through `scene.add_sensor(...)`, and it inherits every imperfection feature (noise, bias, random walk, delay, jitter, history) from `SimpleSensorArray`, which applies them uniformly.

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
import torch

import genesis as gs
from genesis.engine.sensors.base_sensor import (
    LinkAttachedSensorMixin,
    RigidSensorArrayMixin,
    SimpleSensor,
    SimpleSensorArray,
)

from .options import MyProximity


class MyProximitySensorArray(RigidSensorArrayMixin, SimpleSensorArray[MyProximity]):
    def build(self):
        # The manager calls build() once per array, every sensor of the type added. Stack the parameters of all of
        # them into one tensor so one computation runs over every sensor.
        super().build()
        self.max_range = torch.tensor(
            [sensor._options.max_range for sensor in self._sensors], dtype=gs.tc_float, device=gs.device
        )

    def _get_return_format(self, options: MyProximity) -> tuple[int, ...]:
        return (1,)  # one scalar per sensor

    def _get_cache_dtype(self) -> torch.dtype:
        return gs.tc_float

    def _update_raw_data(self, raw_data: torch.Tensor):
        pos = self.solver.get_links_pos(self.links_idx)  # (B, n_sensors, 3)
        dist = pos.norm(dim=-1).clamp(max=self.max_range)  # (B, n_sensors)
        raw_data.copy_(dist)  # write in place; the buffer is (B, cols), one column per sensor here


class MyProximitySensor(LinkAttachedSensorMixin, SimpleSensor[MyProximity, MyProximitySensorArray]):
    pass
```

The rest of this page explains why each piece exists and which additional hooks the more elaborate sensors override.

## Classes you write

Every sensor contributes the same three artifacts, plus two optional ones.

- **Options class:** a public dataclass carrying every per-sensor parameter, inheriting `SimpleSensorOptions` (or the appropriate mixin). It is generic-parameterized with the handle class as a forward reference, `SimpleSensorOptions["MyProximitySensor"]`. This is the only object the user constructs.
- **Array class:** the implementation. One instance exists per sensor type and scene; it owns every tensor of the type and computes one step for all its sensors at once. It inherits `SimpleSensorArray[OptionsT]` and overrides the hooks below.
- **Handle class:** what `scene.add_sensor(...)` returns. It inherits `SimpleSensor[OptionsT, ArrayT]` and is usually an empty class body: `read`, `read_ground_truth`, `start_recording` and every setter are inherited and delegate to the array with the sensor's index. Add a method only for a per-sensor query of your own (the surface distance probe exposes its nearest points this way), delegating to the array with `self._idx`.
- **A `NamedTuple` return type (optional):** declare one when the sensor returns several tensors, and pass it as the second type parameter of the array. See [Returning a NamedTuple](#returning-a-namedtuple).
- **A `SharedSensorContext` subclass (optional):** declare one only when this sensor shares an expensive resource with *other* sensor types, and fetch it from the manager in the array's `build`. See [Sharing a resource across sensor types](#sharing-a-resource-across-sensor-types).

The generic signatures are `SensorArray[OptionsT, DataT]` and `Sensor[OptionsT, ArrayT]`: options first, then the data type for the array (`DataT` defaults to `tuple`) and the array type for the handle.

## Registration is automatic

Sensors are never registered by hand. When a `Sensor` subclass names its options class as the first type parameter, `Sensor.__init_subclass__` records the pairing in `SensorManager.SENSOR_TYPES_MAP` the moment the class body runs, and the array class named as the second parameter is what the manager constructs for that type. The user then only ever constructs the options instance and hands it to `scene.add_sensor(...)`, which resolves the handle class, constructs the array of the type on its first sensor, and returns the handle.

That leaves two supported placements:

- **In-tree (built-in sensors):** options in `genesis/options/sensors/*.py`, array and handle in `genesis/engine/sensors/*.py`. Both are imported through their package `__init__`, so the pairing is registered at import.
- **Out-of-tree (third-party plugins):** put your options and sensor in sibling submodules of one package (for example `my_plugin/options.py` and `my_plugin/sensor.py`). As long as your code imports the options module before constructing the options, the framework resolves the handle class transparently on the first `scene.add_sensor(...)` call.

:::{note}
`__init_subclass__` also enforces the contract: a concrete handle that declares its own options class must also declare its array type, and a violation raises `TypeError` at class-definition time, before any scene is built.
:::

## Required overrides

Two overrides are required of every concrete array, and `SimpleSensorArray` adds a third.

- **`_get_return_format(self, options) -> tuple[...]`:** the *shape* of what `read()` produces for a sensor with these options. Shape is per-sensor by design, because options may legitimately determine it (a raycaster's pattern, a camera's resolution, a proximity sensor's probe positions). Return `(N,)` for a single tensor of `N` scalars, or a tuple of tuples such as `((3,), (3,), (3,))` for a multi-tensor return.
- **`_get_cache_dtype(self) -> torch.dtype`:** the dtype of what `read()` produces. Dtype is uniform over the type: the array packs every sensor into one contiguous cache, so all of them share one dtype. If you need different dtypes, use two sensor types.
- **`_update_raw_data(self, raw_data)`:** the `SimpleSensorArray` computation producing the *ground-truth* value of every sensor of the type at the current step. This is its single abstract producing hook.

`raw_data` has shape `(B, cols)`, the batch dimension first and the columns of the sensors laid end to end in sensor order (the columns of sensor `i_s` are `self._cache_slice(i_s)`). Always populate it in place:

```python
def _update_raw_data(self, raw_data):
    pos = self.solver.get_links_pos(self.links_idx)  # (B, n_sensors, 3)
    raw_data.copy_(pos.reshape(pos.shape[0], -1))  # (B, 3 * n_sensors)
```

Hooks are called once per type per step, never per sensor and never per environment, so vectorize accordingly.

## Choosing a base class

| Base | When to use |
|---|---|
| `SimpleSensorArray[OptionsT]` + `SimpleSensor[OptionsT, ArrayT]` | Almost always. The standard per-step pipeline: raw, physics imperfections, transform, hardware imperfections, post-process, delay sampling. |
| `SimpleSensorArray[OptionsT, DataT]` + `SimpleSensor[OptionsT, ArrayT]` | Same pipeline, but `read()` returns an instance of `DataT`, a `NamedTuple`, instead of a single tensor. The IMU is the canonical example. |
| `CameraSensorArray[OptionsT]` + `CameraSensor[OptionsT, ArrayT]` | Camera-style sensors that render an image on `read()`. See [Camera-style sensors](#camera-style-sensors). |
| `SensorArray[OptionsT]` + `Sensor[OptionsT, ArrayT]` | Only when neither standard pipeline fits. Implement `_update_cache` yourself, or set `has_ring_pipeline = False` and override `read` and `read_all` for a type computing its data on read. |

Mixins compose onto the base:

- **`RigidSensorOptionsMixin` / `KinematicSensorOptionsMixin`:** on the options side, for sensors attached to a `RigidEntity` or any `KinematicEntity` respectively. Combine with `SimpleSensorOptions` through multiple inheritance.
- **`LinkAttachedSensorArrayMixin`:** on the array side, for any sensor attached to a link: `self._links` (the link of each sensor, `None` for a static one) and the per-environment pose offsets `offsets_pos` / `offsets_quat`. `RigidSensorArrayMixin` adds the rigid `solver` and the global `links_idx` tensor; `KinematicSensorArrayMixin` buckets the sensors per kinematic solver in `solver_groups`.
- **`LinkAttachedSensorMixin`:** on the handle side, giving the user `set_pos_offset` / `set_quat_offset`.

## Build-time tables

Everything the hooks read is born in `build()`, from all the sensors at once: solver and link references, per-sensor parameters stacked into tensors (`links_idx`, `thresholds`, `max_range`), per-sensor offsets, filter coefficients, and Python flags that gate slow paths. The constructor holds nothing but the resources `destroy` must release after an aborted build (a renderer handle, for instance).

Inside `build()`, `self._sensors` is the list of handles of the type, sorted by entity and indexed by each handle's `idx`, `self._sim` is the simulator (`self._sim._B` the number of environments, 1 when the scene has none), and every option is `sensor._options`. Call `super().build()` first: `SensorArray.build` lays out the caches and the delay tables, and each mixin stacks its own tables before yours.

`SensorArray.build` stacks the read jitter of every sensor (`jitter_ts`), and `SimpleSensorArray.build` the imperfection parameters (`noise`, `bias`, `random_walk`, `resolution`) with the matching `has_any_*` flags, one span per sensor over the columns of its cache. A setter on the handle (`set_noise`, `set_bias`, ...) writes the span of that sensor for the selected environments through `SensorArray._set_field`; follow the same pattern for a setter of your own, taking `i_s` on the array and delegating from the handle with `self._idx`.

## Optional pipeline hooks

`SimpleSensorArray` runs a fixed per-step pipeline and gives every stage a default. Override a stage only when your sensor needs it. The stages run per branch, in this order:

- **Ground-truth branch:** `_update_raw_data`, then `_apply_transform(is_measured=False)`, then `_post_process(is_measured=False)`.
- **Measured branch:** `_update_raw_data`, then `_apply_physics_imperfections`, then `_apply_transform(is_measured=True)`, then `_apply_hardware_imperfections`, then `_post_process(is_measured=True)`, then delay sampling.

Both branches keep their own intermediate-space timeline ring holding post-transform, pre-hardware-imperfection values, so a stateful `_apply_transform` filter always reads previous slots that are clean of hardware noise. The distinction between the three noise stages is where the perturbation physically originates.

- **`_apply_physics_imperfections(self, measured_slot_0, timeline)`:** random fluctuation of the underlying phenomenon that the simulator does not model (genuine drift, fine-scale turbulence on the field). Measured-only, applied before `_apply_transform`, so it propagates through the response model on later steps. Default: no-op.
- **`_apply_transform(self, data, timeline, *, is_measured)`:** a coordinate transform and/or a stateful response model of the *sensor element* (thermal mass, RC time constant, mechanical bandwidth). Called on both branches; the coordinate part runs unconditionally, and you gate an element-specific effect that must not appear in ground truth on `if is_measured:`. Mutate `data` in place; read history with `timeline.at(1)`, `timeline.at(2)`. The IMU uses this for its body-frame alignment rotation; the temperature-grid sensor uses it for an RC filter.
- **`_apply_hardware_imperfections(self, measured_slot_0)`:** the perturbations the readout electronics introduce at the sensor output. `SimpleSensorArray` already implements `noise`, `bias`, `random_walk`, and `resolution` here, gated by the `has_any_*` flags so an all-zero type skips them entirely. Override only for a non-standard model, and call `super()` first for the standard terms:

```python
def _apply_hardware_imperfections(self, measured_slot_0):
    super()._apply_hardware_imperfections(measured_slot_0)
    # Signal-dependent noise floor, resampled each step.
    measured_slot_0 += torch.normal(0.0, self.signal_noise_coeff) * measured_slot_0.abs()
```

For a sensor whose noise is intrinsic to the physics computation (a single kernel pass must produce both the ideal and the noised value because the noise shapes the kernel's branches), override `_update_current_timestep_data(self, ground_truth_slot_0, measured_slot_0)` instead. It writes the ground-truth slot and the noised measured slot in one pass, and the rest of the pipeline still runs on top. A sensor whose current value depends on its previous ground truth (the temperature grid) reads it from `self._ground_truth_cache`, which still holds the previous step when `_update_raw_data` runs.

### Projecting to a different return type

`_post_process(self, tensor, timeline, *, is_measured) -> torch.Tensor` projects from the pipeline-internal intermediate space into the user-facing return space. Override it when the output type differs from the internal representation: a bool threshold on `ContactSensorArray`, a deadband and saturation on `ContactForceSensorArray`. Return the projected tensor; `step` writes it into the return-space ring and delay-samples it.

```python
def _post_process(self, tensor, timeline, *, is_measured):
    return tensor > self.thresholds  # float intermediate, bool return
```

`_get_intermediate_dtype(self)` defaults to `_get_cache_dtype()`, the return dtype. Override it when the computation needs a different dtype: `ContactSensorArray` returns `gs.tc_float` because its kernel counts contacts in float while its return is bool. A projection that preserves the dtype, such as the clamp of `ContactForceSensorArray`, needs no override. The intermediate buffer stays distinct from the return buffer either way, because the timeline ring lives in intermediate space and an `_apply_transform` filter reads its previous slots there.

## Returning a NamedTuple

For a multi-tensor return, declare a `NamedTuple` and pass it as the second type parameter of the array. `_get_return_format` then returns one shape per field, in field order:

```python
class IMUReturnType(NamedTuple):
    lin_acc: torch.Tensor
    ang_vel: torch.Tensor
    mag: torch.Tensor


class IMUSensorArray(RigidSensorArrayMixin, SimpleSensorArray[IMU, IMUReturnType]):
    def _get_return_format(self, options: IMU) -> tuple[tuple[int, ...], ...]:
        return ((3,), (3,), (3,))  # shapes match the NamedTuple field order

    def _get_cache_dtype(self) -> torch.dtype:
        return gs.tc_float  # one dtype across all fields


class IMUSensor(LinkAttachedSensorMixin, SimpleSensor[IMU, IMUSensorArray]):
    pass
```

The array lays the fields of each sensor end to end in its cache and slices them on read; `read()` reconstructs and returns the `NamedTuple`, with the leading batch dimension dropped when the scene has no environments. Each field has shape `([n_envs,] *field_shape)`.

## Sharing a resource across sensor types

An array and a shared context are both manager-held state, but they solve different problems and must not be conflated. An array is *per-type*: it aggregates the per-sensor rows of one type so a single kernel can vectorize over them, and it grows with the number of sensors. A context is *cross-type*: a single resource, `O(1)` in the number of sensors, that several arrays read.

The canonical context is the collision BVH that the raycasters and the raycast-mode tactile sensors cast against. Building it once and letting every array read it avoids rebuilding identical trees per type. A context is purely an optimization: results must be identical whether or not it is shared, so cross-sensor consistency stays the manager's responsibility.

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

    def update(self):  # once per step, before any consuming array steps
        if self.is_active:
            self._bvh.refresh()

    def reset(self, envs_idx):  # on scene.reset()
        if self.is_active:
            self._bvh.flag_rebuild()

    def destroy(self):  # on teardown
        self._bvh = None
```

Fetch it from the manager and activate it in `build()`, and read it from the producing hooks:

```python
class MySensorArray(SimpleSensorArray[MyOptions]):
    def build(self):
        super().build()
        self._bvh_context = self._manager.get_context(MyBVHContext)
        self._bvh_context.activate()  # idempotent; the first consumer builds the resource

    def _update_raw_data(self, raw_data):
        raw_data.copy_(query(self._bvh_context.bvh, ...))
```

Every array asking for the same context class shares one instance, constructed by the manager on the first request. The manager refreshes every active context once per step before the arrays step, so a context read inside `_update_raw_data` is already current.

## Camera-style sensors

`CameraSensorArray` is a `SensorArray`-direct subclass that codifies the render-on-read pattern of every built-in camera (`RasterizerCameraSensor`, `RaytracerCameraSensor`, `BatchRendererCameraSensor`). Use it for any sensor that produces an image by rendering the scene rather than by reading physics signals each step. It gives you:

- **Render-on-read with frames kept between reads:** a read renders again once the scene stepped since the last render or a reset restored a state, and serves the frames of the last render otherwise, so you never implement `_update_cache`. Several `read()` calls in one step share a single render.
- **Link attachment** with `pos` / `lookat` / `up` or an authored `offset_T`, handing you the world-space transform of each camera to apply to your renderer.
- **An RGB output** of shape `([n_envs,] h, w, 3)` and dtype `torch.uint8`, declared from `options.res`, returned as a `CameraReturnType` `NamedTuple`.

It opts out of the ring pipeline (`has_ring_pipeline = False`) and rejects `delay`, `jitter`, and `history_length` when the sensor is added, since those depend on the per-step storage it does not allocate. Implement two hooks on the array; the handle derives from `CameraSensor` and needs no body:

```python
class MyCameraSensorArray(CameraSensorArray[MyCameraOptions]):
    def _apply_camera_transform(self, i_s: int, camera_T: torch.Tensor) -> None:
        # camera_T is the world-space transform of camera i_s, (4, 4) or (B, 4, 4). Apply it to your renderer.
        ...

    def _render_current_state(self, i_s: int, envs_idx) -> torch.Tensor:
        # Render camera i_s in the selected environments and return their frames, stacked in environment order.
        ...


class MyCameraSensor(CameraSensor[MyCameraOptions, MyCameraSensorArray]):
    pass
```

A backend rendering every camera of the type in one pass (the batch renderer) sets `has_batch_render = True` and, in `_render_current_state`, also writes the frames of the other cameras into their `self.images` entry; the array then records the render for all of them. See `RasterizerCameraSensorArray` for a complete worked example. The standard imperfection knobs are unavailable here; any imperfection model must live inside `_render_current_state`. For non-RGB output (depth, segmentation, normals), override `_get_return_format` / `_get_cache_dtype` and adapt the backing store, or drop down to a bare `SensorArray` subclass.

## What the built-in sensors override

To pick the right hooks, mirror the closest built-in sensor. Every array implements `_get_return_format` and `_get_cache_dtype`; the table shows the additional overrides.

| Array | `_update_raw_data` | `_apply_transform` | `_post_process` (+ intermediate) |
|---|---|---|---|
| `JointTorqueSensorArray` | yes | - | identity; return `(n_dofs,)` float |
| `ContactSensorArray` | yes | - | bool threshold; return `(1,)` bool, intermediate float via `_get_intermediate_dtype` |
| `ContactForceSensorArray` | yes | - | clamp and deadband; dtype preserved |
| `IMUSensorArray` | yes | yes (body-frame alignment) | identity; `NamedTuple` return |
| `RaycasterSensorArray` (Raycaster and DepthCamera) | yes | - | identity |
| `TemperatureGridSensorArray` | yes | yes (RC filter reading `timeline.at(1)`) | identity |
| Any `*CameraSensorArray` | - | - | identity; derives from `CameraSensorArray` |

Every `SimpleSensorArray` inherits `_apply_hardware_imperfections` unchanged; override it only for a non-standard imperfection model.

## Things to double-check

- **Populate `raw_data` in place; never rebind it.** Assigning `raw_data = something_new` leaves the framework-owned buffer untouched and silently breaks the pipeline. Write via `raw_data.copy_(...)`, `raw_data[...] = ...`, or a kernel that takes it as an output argument.
- **Reads are idempotent.** Do not mutate state inside `read()`. State changes belong in the per-step hooks the manager calls once per step.
- **Hooks run once per type, not per sensor or per environment.** Vectorize over the tables stacked at build.
- **Everything is born in `build()`.** No table is grown sensor by sensor; `build` sees every sensor of the type and stacks them at once.
- **Shape is per-sensor; dtype is uniform over the type.** `_get_return_format` takes the options of one sensor so they can affect its shape; `_get_cache_dtype` and `_get_intermediate_dtype` take none because every sensor shares one dtype.
- **Reuse the codebase utilities.** `indices_to_mask` and `tensor_to_array` from `genesis.utils.misc`, and the conventions every built-in sensor follows.

## See also

- {doc}`sensor_pipeline`: how the pipeline executes at runtime, and the intermediate-versus-return separation in full.
- {doc}`/user_guide/sensing/index`: using the built-in sensors.
