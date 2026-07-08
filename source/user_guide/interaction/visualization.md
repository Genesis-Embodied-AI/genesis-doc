# Visualization

This page covers watching a Genesis World scene as it runs: the interactive **viewer** window, and the `gs` command-line tools that open it without writing a script. Reach for these while developing on a machine with a display. To render images off-screen (color, depth, segmentation, video) or produce photorealistic frames, see {doc}`Rendering </user_guide/rendering/rendering>`.

Every scene owns a `visualizer` (`scene.visualizer`) that drives both the viewer and camera sensors. The viewer runs in its own thread and follows the simulation in real time; camera sensors render frames on demand and work headless (see {doc}`Rendering </user_guide/rendering/rendering>`).

## The viewer

Configure the scene's visuals through two options objects. `viewer_options` controls the interactive window; `vis_options` controls visual properties shared by the viewer *and* every camera (frame gizmos, lighting, reflections). Pass `show_viewer=True` to open the window:

```python
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        res=(1280, 960),
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,  # draw the world coordinate frame at the origin
        world_frame_size=1.0,  # length of each axis, in meters
        show_link_frame=False,  # do not draw per-link frames
        show_cameras=False,  # do not draw camera meshes and frustums
        plane_reflection=True,
        ambient_light=(0.1, 0.1, 0.1),
    ),
    show_viewer=True,
)
```

`camera_pos` and `camera_lookat` are in meters, in the right-handed, Z-up world frame. `camera_fov` is the vertical field of view in degrees. If `res` is `None`, Genesis World opens a 4:3 window sized to half your display height.

The viewer always renders with the rasterizer. To select the backend used by camera sensors (rasterizer, ray tracer, or batch renderer), see {doc}`Rendering backends </user_guide/rendering/rendering>`.

:::{note}
To cap the viewer frame rate, set `refresh_rate` on `ViewerOptions`. The older `max_FPS` argument is deprecated and now maps to `refresh_rate`.
:::

Once the scene exists, reach the viewer through the `scene.viewer` shortcut to read or set the camera pose at runtime:

```python
pose = scene.viewer.camera_pose
scene.viewer.set_camera_pose(pos=(3.5, 0.0, 2.5), lookat=(0, 0, 0.5))
```

## Command-line tools

Installing Genesis World adds a `gs` command with a few subcommands, so you can open the viewer without writing a script. Run `gs` with no arguments to list them.

**`gs launch [asset]`** opens an asset in the interactive viewer. It accepts a Mesh, URDF, MJCF, or USD file; for a USD stage, every rigid entity in the stage is loaded. The viewer's overlay exposes per-joint sliders and play, pause, step, and reset controls, and it starts paused so you can inspect and pose the asset first. With no file, it opens an empty scene to which you can add entities live. Useful flags: `-c` visualize collision geometry, `-r` slowly rotate the asset, `-s SCALE` scale it, and `-l` show link frames.

```bash
gs launch xml/franka_emika_panda/panda.xml
```

**`gs play [asset]`** opens the same interactive viewer but runs the physics simulation, so joints and bodies respond under gravity and contact. With no file, it loads a demo scene (a Franka arm on a ground plane). It accepts `-c` and `-s SCALE`.

```bash
gs play xml/franka_emika_panda/panda.xml
```

**`gs animate 'pattern'`** combines every image matching a glob pattern into a video written to `video.mp4`. Pass `--fps` to set the frame rate (default 30).

```bash
gs animate 'frames/*.png' --fps 60
```

:::{note}
`gs view` still works as a deprecated alias of `gs launch` and prints a deprecation warning. Use `gs launch` instead.
:::

## Next steps

- {doc}`Rendering </user_guide/rendering/rendering>`: cameras, image types, video, lighting, and rendering backends.
- {doc}`Interactive GUI and debugging </user_guide/interaction/interactive_debugging>`: inspecting objects, drawing debug geometry, and the in-viewer control panel.
- {doc}`Viewer interaction and plugins </user_guide/interaction/viewer_plugin>`: extending the viewer with keybindings and plugins.
