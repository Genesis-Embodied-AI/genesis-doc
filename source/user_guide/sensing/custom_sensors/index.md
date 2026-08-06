# Custom sensors

The {doc}`sensor overview </user_guide/sensing/index>` covers the user-facing side: attach a sensor with `scene.add_sensor()`, step the simulation, and read a tensor. This section is for the other side of that boundary. Read it when the built-in sensors are not enough and you need to add your own type, or when you want to understand what happens between `scene.step()` and the value `sensor.read()` hands back.

The overview treats a sensor as a device you configure and query; here a sensor is a small pipeline you implement. Imperfections, delay, history, and idempotent reads all come out of that pipeline, so behavior a user relies on is behavior an author has to reproduce correctly.

- **{doc}`sensor_pipeline`:** the runtime model. It follows one measurement from the physics state through the per-step pipeline to `read()`, and explains why `read()` is a constant-time memory lookup rather than an acquisition.
- **{doc}`custom_sensors`:** the author's guide. It covers which hooks to override, the shape and dtype contracts each must honor, and the automatic plugin registration that pairs an options class with its sensor class.

Start with {doc}`sensor_pipeline` if you want the mental model first; jump to {doc}`custom_sensors` if you already understand the pipeline and want the contract.

```{toctree}
:hidden:
:maxdepth: 1

sensor_pipeline
custom_sensors
```
