# Troubleshooting

Find the error or symptom below and check its likely causes first. If the problem persists, capture a failing run and attach it to a bug report. For installation problems, such as a missing GPU backend or a black viewer window, see {doc}`Installation <installation>`.

## The simulation raises an error

The rigid solver checks for errors periodically and raises a `gs.GenesisException` that names the cause.

**`Invalid constraint forces causing 'nan'` or `Invalid accelerations causing 'nan'`.** The integration became unstable. Reduce `dt`, or increase `substeps` in `SimOptions`. {doc}`Tuning simulation parameters </user_guide/configuration/simulation_tuning>` explains how to choose them.

**`Exceeding max number of candidate contact points`.** Increase `max_collision_pairs` in `RigidOptions`.

**`Exceeding max number of post-pruning contact points`.** Increase `max_contacts` in `RigidOptions`.

**`Collision detection reported a contact whose position, normal or penetration is not finite`.** This is an internal solver error. Capture the run as described below and report it.

## Objects pass through each other or jitter

- **Thin or fast objects pass through.** Reduce `dt` or increase `substeps`, so that an object moves less than its own thickness in one substep.
- **Resting objects jitter or creep.** Compare `friction_cone=gs.friction_cone.elliptic` in `RigidOptions` after checking the collision geometry and integration interval. {doc}`Rigid bodies </user_guide/physics/rigid_bodies>` explains the friction options.
- **A robot collides with itself at rest.** Check the collision geometry with `gs launch robot.urdf -c`, which shows the collision meshes in the viewer.

## The first run is slow

Genesis World compiles its GPU kernels the first time a scene builds, and caches them for later runs. The first `scene.build()` of a new scene is therefore slow. Later builds of the same scene load the cached kernels and start faster. {doc}`Initialization </user_guide/configuration/initialization>` lists the options that affect compile time.

## Capture a failing run

Include the reproducing script and, when supported, a `.gstraj` file containing the scene and simulation state. Checkpoint and trajectory files support rigid and kinematic scenes; scenes with unsupported entities, such as soft bodies, or an IPC coupler need a reproducing script instead. See {doc}`Checkpoints and simulation state </user_guide/configuration/checkpoints>` for supported contents and recording options.

### Save a checkpoint

Save the state when you detect a problem, for example around the step loop:

```python
try:
    for i in range(10_000):
        scene.step()
except gs.GenesisException:
    scene.save_checkpoint("failing.gstraj")
    raise
```

A checkpoint preserves the state at the failure for inspection. If the problem develops over several steps, register a trajectory recorder before `scene.build()` so the recording also captures the lead-up:

```python
scene.start_recording(gs.recorders.TrajectoryFile(filename="run.gstraj"))
scene.build()
for _ in range(1000):
    scene.step()
scene.stop_recording()
```

The {doc}`checkpoints guide </user_guide/configuration/checkpoints>` covers recording modes, file size limits, and loading a checkpoint or trajectory from Python.

### Inspect the recording

Watch the recorded frames in the viewer:

```bash
gs replay run.gstraj
```

Replay displays the saved run. To test a change in solver settings, geometry, or control, rerun the reproducing script with that change. Seeking a recorded frame also restores its recorded model parameters.

The file leaves out sensors, cameras, and pre-step callbacks, and Genesis World logs a warning that names them. If you continue simulating from a restored state, register callbacks that issue commands or pause the simulation, and supply future commands from any external control loop again. The file loaders return built scenes, so sensors cannot be added afterward. If your controller needs an omitted sensor, rerun the original script with its sensor setup to reproduce the failure.

## Report the bug

Open an issue with the [bug report template](https://github.com/Genesis-Embodied-AI/genesis-world/issues/new/choose). Include:

- The smallest script that reproduces the problem, with its model assets or links to them.
- The `.gstraj` file, if the scene supports checkpointing or trajectory recording.
- The full log output, including the Genesis World version and backend.
- The expected behavior and what happened instead.

Set `debug=True` in your existing `gs.init(...)` call when capturing the log. This enables debug logging and deterministic execution on the CPU backend.
