# Checkpoints and simulation state

A simulation has two things worth keeping. The first is its *dynamic state*: the numbers the physics solvers advance every step, such as joint positions, velocities, and particle fields. Capturing that state and restoring it later lets you rewind a simulation or reset an environment between episodes, deterministically, from the exact state you left. The second is the *scene itself*: the entities, their geometry, and every option the scene was created with. Writing that to a file lets someone else open the very scene you built, on a machine holding none of the assets you built it from.

Genesis World offers four ways to keep them, which answer different needs.

- **Dynamic state, in memory:** `scene.get_state()` returns a {py:class}`SimState <genesis.engine.states.solvers.SimState>` object, and `scene.reset(state=...)` writes it back. Fast, and the basis of episode resets in reinforcement learning.
- **The whole scene and its state, in memory:** the pickle protocol. `pickle.dumps(scene)` gives a built copy that steps on exactly as the original, and `scene.__getstate__()` and `scene.__setstate__()` save and restore a built scene in place. Use it to checkpoint a run, or to hand a scene to another process.
- **The scene, on disk:** `scene.export(path)` writes a `.gscene` file, and `gs.Scene.load(path)` opens it into a new scene, ready to build. Use it to share a scene, attach one to a bug report, or rebuild one without its assets.
- **A run, on disk:** `scene.save_checkpoint(path)` writes the scene with every array of its simulation, and `scene.start_recording(gs.recorders.TrajectoryFile(...))` writes a frame per step. `gs.Scene.load_checkpoint(path)` and `gs.Scene.load_trajectory(path)` open them in a built scene, to resume, seek, and replay, on any machine and backend.

A state snapshot assumes the scene it came from is already built. A scene file carries no simulated state, so a scene opened from one stands at the configuration its entities were given, and the state has to be reproduced by stepping it again. A checkpoint or a trajectory carries both, so the scene it opens stands where the recorded one stood.

## State model

A snapshot captures only the *dynamic* state: the fields that change as the simulation steps. It does not capture the scene's *structure*: the entities, their morphs, the solver options, or the number of environments. That structure is fixed by how you build the scene, and restoring a snapshot assumes it is already in place.

- **`SimState`:** the object returned by `scene.get_state()`. It holds one per-solver state object for each active solver, batched over environments.
- **Dynamic state:** positions, velocities, and the internal fields each solver integrates. This is what a snapshot holds.
- **Static structure:** entities, morphs, geometry, and solver configuration. A snapshot leaves it out, and a scene file is how it travels (see below).

Because structure is not part of the snapshot, a snapshot is only valid for the scene it was taken from, or one built the same way. Restoring into a scene with different entities or solver options is undefined.

## Snapshot and restore in memory

`scene.get_state()` reads the current state into a `SimState`. `scene.reset()` returns the scene to a stored initial state, and `scene.reset(state=...)` restores an arbitrary snapshot:

```python
scene.build()

for _ in range(100):
    scene.step()

state = scene.get_state()  # snapshot the state at step 100

for _ in range(50):
    scene.step()

scene.reset(state=state)  # rewind to the snapshot; the physics continue from there
```

A reset also sets the simulated time of the environments it touches back to zero, whichever snapshot it restores, so `scene.get_time()` counts from the reset rather than from the build.

:::{warning}
Passing `state` to `reset()` also registers it as the scene's initial state. A subsequent bare `scene.reset()` returns to *this* snapshot, not to the state the scene had at build time. Keep a separate reference to your build-time state if you need both.
:::

The per-solver state objects are plain attribute holders. The rigid solver's state carries `qpos`, `dofs_vel`, `links_pos`, and `links_quat`; reading one field looks like this:

```python
state = scene.get_state()
rigid_state = state.solvers_state[scene.solvers.index(scene.rigid_solver)]
qpos = rigid_state.qpos  # shape ([n_envs,] n_qs)
```

The differentiable example [`examples/deformable/differentiable_push.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/deformable/differentiable_push.py) uses this pattern: it calls `scene.reset()` to restart each optimization pass from a fixed initial state, and reads `scene.get_state().solvers_state[...]` to compute a loss from particle positions mid-rollout.

## Resetting environments in parallel simulation

In {doc}`parallel simulation </user_guide/getting_started/parallel_simulation>`, the state is batched over environments, and `reset()` takes an `envs_idx` argument so you can reset a subset without disturbing the rest. This is the mechanism behind per-environment episode resets in reinforcement learning: when some environments finish, you restore only those to the initial state and let the others keep running.

```python
scene.build(n_envs=4096)

init_state = scene.get_state()  # the state all environments reset to

for step in range(episode_length):
    scene.step()
    obs, reward, done = get_observations()

    if done.any():
        done_envs = torch.where(done)[0]  # indices of finished environments
        scene.reset(state=init_state, envs_idx=done_envs)
```

- **`envs_idx`:** the environments to reset, as any array-like of indices. `None` (the default) resets every environment.
- **Partial reset:** with `envs_idx`, only the selected environments take the new state; the others advance uninterrupted.

`envs_idx` applies only to a scene built with environments, so on a non-parallelized scene it raises.

## Sharing a scene as a file

`scene.export(path)` writes what the scene was authored from and what its build resolved: every entity's description, with its geometry, textures and physical coefficients, beside every option the scene was created with. No filesystem path goes into the file, so it opens on a machine holding none of the meshes, model files or textures the scene came from. `gs.Scene.load(path)` creates that scene, holding every entity it was authored with and waiting to be built:

```python
# Wherever the scene was authored.
scene = gs.Scene()
scene.add_entity(gs.morphs.Plane())
robot = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))
scene.export("franka.gscene")
```

```python
# Anywhere else, with no asset on disk.
scene = gs.Scene.load("franka.gscene")
scene.build(n_envs=16)
scene.step()
```

Adding an entity resolves its description, so a scene is exported before it is built as readily as after, and the number of environments is chosen by whoever builds the loaded scene. A scene file is the right thing to attach to a bug report: a maintainer opens it and steps the exact scene you had, with none of your script and none of your assets.

The file names what it holds rather than carrying code to run. Genesis World creates only the options, descriptions and meshes the file declares, and rejects a value that contradicts its declared type, so a scene from a stranger is safe to open. A load also compares the layout of every class the file holds with the current one, and refuses a file written when a class meant something else, naming the class. A file written by another version of Genesis World whose classes still match loads with a warning that the simulation it describes may run differently.

Every option the scene was created with travels as one {py:class}`SceneOptions <genesis.options.scene.SceneOptions>` object, reachable as `scene.options` on any scene. Passing it to `gs.Scene(options=other.options)` creates a scene from what another was created with, which is also how a loaded scene gets its options back. The physics options stand as recorded, since they size the arrays a recorded state fills. The viewer and visualizer options passed at load override the recorded ones for the fields they set, while every other field keeps its recorded value, and a renderer passed at load replaces the recorded one as a whole. A scene recorded headless thus opens in the viewer a debugging session needs:

```python
scene = gs.Scene.load(
    "franka.gscene",
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(camera_pos=(2.0, 1.5, 1.0), camera_lookat=(0.0, 0.0, 0.3)),
)
```

What a description carries is what travels, and `export` tells you about the rest:

- **Refused, by name:** anything that alters the simulation and that a description leaves out, since a file without it would restore other physics: an emitter, a force field, and any entity that carries no description, which is every entity that is neither rigid nor kinematic.
- **Written without, with a warning naming it:** what observes or draws the simulation rather than shaping it. A camera, a recorder, a sensor, a callback Genesis World calls at every step, a texture read from an HDR or EXR file, and the visual vertices an entity was given at runtime. Add those back on the loaded scene.

## Checkpointing a built scene

A `SimState` holds what you read back as positions and velocities. A **checkpoint** holds everything a step reads from one step to the next: the reduced-space state and the control inputs, the contacts and the constraint solution, the warm-start caches, and the link and geom poses the last step derived. Stepping a restored scene therefore lands bit-for-bit where the original went, on every backend.

The checkpoint is the pickle protocol. `scene.__getstate__()` returns a {py:class}`SceneCheckpoint <genesis.engine.scene.SceneCheckpoint>`: the scene description, the environment layout the scene was built with, and the arrays of every solver, copied where they live, so a save and a restore within one process stay on the device. `scene.__setstate__(checkpoint)` puts a scene built from the same description and layout back in that state, and rejects a checkpoint from another build by the name of what differs. Pickling a scene reads the same record, and unpickling creates and builds the scene before restoring it:

```python
import pickle

scene.build(n_envs=16)
for _ in range(100):
    scene.step()

checkpoint = scene.__getstate__()  # a device-resident copy of the state at step 100
twin = pickle.loads(pickle.dumps(scene))  # a built copy of the scene, standing at step 100

for _ in range(50):
    scene.step()
scene.__setstate__(checkpoint)  # back to step 100, and the next 50 steps land where they did
```

A restore also restarts what surrounds the state, as a reset does: the gradient tape, the sensors, and the recorders forget the run that led there, and the viewer redraws. The simulated time of each environment comes back as recorded, since it is state. A differentiable scene carries the gradients of its arrays along, so a checkpoint taken after a backward pass restores them.

## Checkpoint and trajectory files

`scene.save_checkpoint(path)` writes a `.gstraj` file holding the scene as `export` writes it and every array of the simulation, scratch buffers included, so the exact state of a failing run is kept for inspection. `gs.Scene.load_checkpoint(path)` creates and builds the scene and restores that state:

```python
scene.save_checkpoint("failing.gstraj")
```

```python
scene = gs.Scene.load_checkpoint("failing.gstraj", show_viewer=True)
scene.step()  # continues from the saved state
```

A **trajectory** is a checkpoint per step. Register a {py:class}`TrajectoryFile <genesis.options.recorders.TrajectoryFile>` with `scene.start_recording` before the build, and every step appends a frame until `scene.stop_recording()`, which also records the state the run stopped at:

```python
scene.start_recording(gs.recorders.TrajectoryFile(filename="run.gstraj"))
scene.build()
for _ in range(1000):
    scene.step()
scene.stop_recording()
```

The writer runs on the stepping thread, so every frame is kept, and compresses and writes each completed chunk on a thread of its own while the simulation steps on. Two modes trade size for exactness, and `exact` picks one:

- **Exact** (the default for a single environment): every frame holds everything a step reads or writes, so a replay is bit-for-bit and the simulation resumes from any frame.
- **Compressed** (the default for a batched scene, with a warning): every frame holds the model parameters, configuration, velocities, accelerations, control inputs, contacts, and constraint forces. The file is several times smaller, and a load recomputes the link and geom poses by forward kinematics, which may differ at the last bits.

`hz` records every few steps, `chunk_size` sets how many frames a chunk holds (larger chunks compress better and seek slower), and `max_size` caps the file, closing it as a valid log and raising at the next step past the cap, so a run left recording fills the disk by at most 2 GiB by default.

`gs.Scene.load_trajectory(path)` creates and builds the recorded scene and returns a {py:class}`Trajectory <genesis.recorders.trajectory.Trajectory>` that plays in it. Frame `i` is the state after `i` steps; `seek(i)` puts the scene there, `play()` seeks every frame and redraws the viewer at the pace the recording ran at, `frame(i)` returns the arrays of a frame by name, and `time(i)` the simulated time of each environment. A negative index counts from the end. The last frame, like a checkpoint file, holds every array but the configs and constants, the scratch of the solvers included, for the analysis of a failure that may depend on the platform and never reproduce once shared:

```python
trajectory = gs.Scene.load_trajectory("run.gstraj", show_viewer=True)
trajectory.seek(500)
trajectory.scene.step()  # steps on from frame 500 as the recorded run did
trajectory.play(loop=True)  # replays until the viewer is closed
```

A trajectory replays on another machine, backend, or precision: the frames are shaped by the options, the description, and the number of environments, and their values are cast to the precision of the session. From the command line, `gs replay run.gstraj` opens the recorded scene in the viewer and plays it in a loop.

## What a snapshot contains

The dynamic state each solver contributes to a `SimState`:

| Solver | State fields |
|---|---|
| Rigid | `qpos`, `dofs_vel`, `dofs_acc`, `links_pos`, `links_quat`, `friction_ratio` |
| Kinematic | `qpos`, `dofs_vel`, `links_pos`, `links_quat` |
| MPM | `pos`, `vel`, `C`, `F`, `Jp`, `active` |
| SPH | `pos`, `vel`, `active` |
| PBD | `pos`, `vel`, `free` |
| FEM | `pos`, `vel`, `active` |

## Reproducibility notes

- **Configuration must match.** A snapshot restores fields by position into an already-built scene. The entities, solver options, and environment count must match the scene that produced it. There is no compatibility check: a mismatch fails or silently corrupts state. A checkpoint or a trajectory frame restores arrays by name and checks their shapes, so one from another build is rejected and named. Both also carry a digest of the scene description, its entities and physics options, and restore only into a scene sharing it, whatever its viewer, visualizer and renderer options. The digest exports the description in memory, meshes included, once per built scene and once per trajectory opened, never per restore.
- **Precision limits exactness.** Genesis World uses 32-bit floats by default (see {doc}`initialization`). Reproducing a run by stepping a loaded scene, or restoring a snapshot that went through a file, is therefore accurate to roughly single precision, not bit-exact. Initialize with `precision="64"` if you need tighter reproducibility.

## See also

- {doc}`Parallel simulation </user_guide/getting_started/parallel_simulation>`: how state is batched over environments.
- {doc}`Scene API </api_reference/engine/scene>`: the full signatures of `get_state`, `reset`, `export`, `load`, `save_checkpoint`, `load_checkpoint`, and `load_trajectory`.
- {doc}`Recording data </user_guide/sensing/recorders>`: the recorder framework a trajectory is recorded through.
