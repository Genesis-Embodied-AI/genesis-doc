# 📏 Proximity

The `Proximity` sensor reports the nearest distance from one or more local probe positions to a selected set of tracked rigid links. Each probe returns the nearest point on any tracked mesh surface within `max_range`.

```python
sensor = scene.add_sensor(
    gs.sensors.Proximity(
        entity_idx=robot.idx,
        link_idx_local=robot.get_link("palm").idx_local,
        probe_local_pos=((0.0, 0.0, 0.0),),
        track_link_idx=(duck.base_link_idx, box.base_link_idx),  # global rigid link idx
        max_range=0.5,
        draw_debug=True,
    )
)

scene.build()

distances = sensor.read()        # shape ([n_envs,] n_probes)
points = sensor.nearest_points   # shape ([n_envs,] n_probes, 3)
```

If no tracked mesh is found within `max_range`, the reported distance is clamped to `max_range` and the returned points are the probe positions themselves.

The interactive example at `examples/sensors/proximity_shadowhand.py` mounts proximity probes on the palm and fingertips of a dexterous robot hand.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/proximity.mp4" type="video/mp4">
</video>
