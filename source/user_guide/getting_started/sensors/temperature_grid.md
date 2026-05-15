# 🌡️ Temperature Grid

The `TemperatureGrid` sensor discretizes the bounding box of a rigid link into a 3D voxel grid and returns the temperature of each cell in Celsius. Heat transfer is driven by contact, conduction, radiation, convection, and optional per-cell heat generation.

Provide a `properties_dict` describing the thermal material properties of the links that may participate in heat exchange. Key `-1` can be used as a default entry for links that are not listed explicitly.

```python
temperature_sensor = scene.add_sensor(
    gs.sensors.TemperatureGrid(
        entity_idx=entity.idx,
        link_idx_local=0,
        grid_size=(10, 10, 1),
        properties_dict={
            -1: gs.sensors.TemperatureProperties(
                base_temperature=22.0,
                conductivity=100.0,
                density=1000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
            entity.base_link_idx: gs.sensors.TemperatureProperties(
                base_temperature=200.0,
                conductivity=1000.0,
                density=2000.0,
                specific_heat=1.0,
                emissivity=0.8,
            ),
        },
        ambient_temperature=22.0,
        convection_coefficient=0.0,
        draw_debug=True,
    )
)

scene.build()

grid = temperature_sensor.read()
print(grid)  # shape ([n_envs,] nx, ny, nz)
```

Set `simulate_all_link_temperatures=True` if you want Genesis to evolve temperatures for every link with thermal properties, not just the sensor-attached link.

The example `examples/sensors/temperature_grid.py` visualizes a hot pusher heating a platform while objects are dropped onto the sensorized surface.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/temperaturegrid.mp4" type="video/mp4">
</video>
