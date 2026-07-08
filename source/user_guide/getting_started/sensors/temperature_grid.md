# Temperature grid

The `TemperatureGrid` sensor overlays a 3D voxel grid on one rigid link and reports the temperature of every cell, in degrees Celsius. Genesis World discretizes the link's local bounding box into an `(nx, ny, nz)` grid and evolves each cell's temperature from contact conduction, radiation, convection, and optional per-cell heat generation. Use it to observe how a surface heats or cools as other bodies touch it.

The complete script is [`examples/sensors/temperature_grid.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/sensors/temperature_grid.py), an interactive scene in which a hot pusher and dropped objects heat a sensorized platform.

## Minimal example

A temperature sensor attaches to one link of a rigid {doc}`entity </api_reference/entity/index>`. `entity_idx` selects the entity and `link_idx_local` the link within it; `grid_size` sets the resolution as `(nx, ny, nz)`.

```python
temperature_sensor = scene.add_sensor(
    gs.sensors.TemperatureGrid(
        entity_idx=platform.idx,
        link_idx_local=0,
        grid_size=(10, 10, 1),  # (nx, ny, nz) voxels over the link's local bounding box
        properties_dict=properties_dict,
        ambient_temperature=22.0,  # °C
        convection_coefficient=0.0,  # W/(m²·K); 0.0 disables surface cooling
        draw_debug=True,
        debug_temperature_range=(0.0, 80.0),  # °C mapped to the blue→red debug colors
    )
)

scene.build()
```

After the scene is built, `read()` returns the current temperature field:

```python
data = temperature_sensor.read()  # shape ([n_envs,] nx, ny, nz), in °C
t_min, t_max = float(data.min()), float(data.max())
```

The `[n_envs,]` axis is present only when the scene is built with multiple {doc}`environments </user_guide/getting_started/parallel_simulation>`; a single-environment scene returns a plain `(nx, ny, nz)` tensor.

## Material properties

Heat only flows between links that carry thermal properties. You supply these through `properties_dict`, which maps a global rigid-link index to a `TemperatureProperties` entry. Key `-1` is the default applied to any link not listed explicitly; omit it and unlisted links are ignored in contacts entirely.

```python
properties_dict = {
    -1: gs.sensors.TemperatureProperties(  # default for unlisted links
        base_temperature=-40.0,
        conductivity=200.0,
        density=2000.0,
        specific_heat=1.0,
        emissivity=0.85,
    ),
    platform.base_link_idx: gs.sensors.TemperatureProperties(
        base_temperature=22.0,  # room temperature
        conductivity=100.0,
        density=1000.0,
        specific_heat=0.2,
        emissivity=0.4,
    ),
    pusher.base_link_idx: gs.sensors.TemperatureProperties(
        base_temperature=200.0,  # hot
        conductivity=1000.0,
        density=2000.0,
        specific_heat=1.0,
        emissivity=0.8,
    ),
}
```

Each field has a fixed unit:

| Field | Meaning | Unit |
|---|---|---|
| `base_temperature` | Resting temperature of the material | °C |
| `conductivity` | Thermal conductivity | W/(m·K) |
| `density` | Mass density | kg/m³ |
| `specific_heat` | Specific heat capacity | J/(kg·K) |
| `emissivity` | Radiative emissivity, `0`–`1` | — |

`properties_dict`, `ambient_temperature`, and `convection_coefficient` are shared across every temperature sensor in the scene: the dictionaries are merged, and the last ambient and convection values set win.

## Behavior and guarantees

- **Frame and layout.** The grid is defined in the link's local frame and spans its bounding box, so it moves and rotates with the link. Cell `(0, 0, 0)` is the corner of the bounding box; `grid_size=(10, 10, 1)` is a single-layer 10×10 sheet, useful for a flat surface like the platform above.
- **Units.** All temperatures are in degrees Celsius, on input (`base_temperature`, `ambient_temperature`) and on output (`read()`). `ambient_temperature` defaults to 21 °C.
- **Convection.** `convection_coefficient` is the surface cooling coefficient *h* in W/(m²·K) and defaults to 1.0. Set it to 0.0 to disable convective cooling, as the example does.
- **Unlisted links.** With `simulate_all_link_temperatures=False` (the default), links other than the sensor's own are treated as adiabatic: they exchange no heat and stay at their `base_temperature`. Set it to `True` to evolve the temperature of every link that has thermal properties; the per-link values are then available on the `link_temperatures` attribute.
- **Heat generation.** Pass `heat_generation` (a per-cell array matching `grid_size`, in W/m²) to inject heat into specific cells, for example to model a heating element embedded in the link.

:::{tip}
`draw_debug=True` colors each cell in the viewer from blue (cool) to red (hot), mapped across `debug_temperature_range` in °C. It is a visualization aid only and does not affect the values `read()` returns.
:::

<video preload="auto" controls="True" width="100%">
<source src="../../../_static/videos/temperaturegrid.mp4" type="video/mp4">
A hot pusher and dropped objects heat a sensorized platform, whose temperature grid shifts from blue to red at the contact regions.
</video>

## See also

- {doc}`Sensors <index>`: the sensor pipeline, batched reads, and history.
- {doc}`Recorders <../recorders>`: saving sensor data alongside the simulation.
