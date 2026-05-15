# 🔬 Sensors

The internal pipeline that produces sensor measurements, and the contract for extending Genesis with custom sensor types. Read these pages if you are implementing a new sensor or want to understand the abstractions behind `sensor.read()`.

- [**Sensor Pipeline**](sensor_pipeline) - the runtime data flow: embedded-sampler abstraction, intermediate vs. return space, per-step orchestration, eager `_post_process`, storage scopes.
- [**Implementing Custom Sensors**](custom_sensors) - the writer's guide: which hooks to override, shape/dtype contracts, automatic plugin registration, worked examples (including camera-style sensors via `BaseCameraSensor`).

```{toctree}
:hidden:
:maxdepth: 1

sensor_pipeline
custom_sensors
```
