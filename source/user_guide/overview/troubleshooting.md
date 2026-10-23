# Troubleshooting

This page covers problems that appear while a simulation runs, and how to capture a failing run so that someone else can reproduce it. For problems during installation, such as a missing GPU backend or a black viewer window, see {doc}`Installation → Troubleshooting <installation>`.

## Capture a failing run

A bug report that includes the exact scene and state is much faster to fix than a description. Genesis World can write both to a `.gstraj` file, which opens on another machine or backend.

### Save the state at the failure

`scene.save_checkpoint(path)` writes the scene description and every simulation array to one file. Call it when you detect the problem, for example in an `except` block around the step loop:

```python
try:
    for i in range(10_000):
        scene.step()
except gs.GenesisException:
    scene.save_checkpoint("failing.gstraj")
    raise
```

To open the saved state, call `gs.Scene.load_checkpoint`. It creates and builds the scene, and the next `scene.step()` continues from the saved state:

```python
scene = gs.Scene.load_checkpoint("failing.gstraj", show_viewer=True)
scene.step()
```

### Record the run that leads to the failure

A checkpoint shows the state at one step. If the problem builds up over time, record every step instead:

1. Create the scene and add its entities.
2. Call `scene.start_recording(gs.recorders.TrajectoryFile(filename="run.gstraj"))` before `scene.build()`.
3. Build the scene and run your step loop.
4. Call `scene.stop_recording()` after the loop.

```python
scene.start_recording(gs.recorders.TrajectoryFile(filename="run.gstraj"))
scene.build()
for _ in range(1000):
    scene.step()
scene.stop_recording()
```

The recorder writes the file in chunks while the simulation runs. If the script crashes, every completed chunk stays readable. By default the file stops growing at 2 GiB; set `max_size` on `TrajectoryFile` for a longer run.

### Replay a recording

To watch a recording in the viewer, run:

```bash
gs replay run.gstraj
```

The command plays the recording in a loop until you close the viewer. Add `-e 0 3` to render only environments 0 and 3, which makes the replay of a large batch faster.

To inspect the recording from Python, open it with `gs.Scene.load_trajectory`. `seek(i)` puts the scene in the state after step `i`, so you can step on from just before the failure:

```python
trajectory = gs.Scene.load_trajectory("run.gstraj", show_viewer=True)
trajectory.seek(500)
trajectory.scene.step()
```

{doc}`Checkpoints and simulation state </user_guide/configuration/checkpoints>` describes the recording modes, file size limits, and what a frame contains.

### What a file cannot hold

`save_checkpoint` and `TrajectoryFile` raise if the scene holds an entity, an emitter, or a force field that has no scene description, since a file without it would restore different physics. The file leaves out sensors, cameras, and pre-step callbacks, and Genesis World logs a warning that names them. Pre-step callbacks can drive controllers or pause the simulation, so register them again before stepping a restored scene to reproduce the original behavior.

### Report the bug

Open an issue with the [bug report template](https://github.com/Genesis-Embodied-AI/genesis-world/issues/new/choose). Attach the `.gstraj` file, the script that produced it, and the full log output. Add `gs.init(debug=True)` when you capture the log, because it raises the log level to `DEBUG` and makes the run deterministic on the CPU backend.

## The simulation raises an error

The rigid solver checks for errors periodically and raises a `gs.GenesisException` that names the cause.

**`Invalid constraint forces causing 'nan'` or `Invalid accelerations causing 'nan'`.** The integration became unstable. Reduce `dt`, or increase `substeps` in `SimOptions`. {doc}`Tuning simulation parameters </user_guide/configuration/simulation_tuning>` explains how to choose them.

**`Exceeding max number of candidate contact points`.** Increase `max_collision_pairs` in `RigidOptions`.

**`Exceeding max number of post-pruning contact points`.** Increase `max_contacts` in `RigidOptions`.

**`Collision detection reported a contact whose position, normal or penetration is not finite`.** This is an internal solver error. Capture the run as described above and report it.

## Objects pass through each other or jitter

- **Thin or fast objects pass through.** Reduce `dt` or increase `substeps`, so that an object moves less than its own thickness in one substep.
- **Resting objects jitter or creep.** Use `friction_cone=gs.friction_cone.elliptic` in `RigidOptions`. {doc}`Rigid bodies </user_guide/physics/rigid_bodies>` explains the friction options.
- **A robot collides with itself at rest.** Check the collision geometry with `gs launch robot.urdf -c`, which shows the collision meshes in the viewer.

## The first run is slow

Genesis World compiles its GPU kernels the first time a scene builds, and caches them for later runs. The first `scene.build()` of a new scene is therefore slow. Later builds of the same scene load the cached kernels and start faster. {doc}`Initialization </user_guide/configuration/initialization>` lists the options that affect compile time.
