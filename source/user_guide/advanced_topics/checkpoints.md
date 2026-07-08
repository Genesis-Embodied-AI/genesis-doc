# Checkpoints and simulation state

A checkpoint is a snapshot of the dynamic state of a scene at one instant: the numbers the physics solvers advance every step, such as joint positions, velocities, and particle fields. Capturing that snapshot and restoring it later lets you rewind a simulation, reset an environment between episodes, or resume a long run after a crash — deterministically, from the exact state you left.

Genesis World exposes two levels of this. The state model is the same underneath; the difference is where the snapshot lives.

- **In memory:** `scene.get_state()` returns a `SimState` object, and `scene.reset(state=...)` writes it back. Fast, and the basis of episode resets in reinforcement learning.
- **On disk:** `scene.save_checkpoint(path)` pickles the full physics state to one file, and `scene.load_checkpoint(path)` restores it into a matching scene. Use it to persist a run across processes.

All of these operate on a built scene. Build first, then snapshot.

## The state model

A snapshot captures only the *dynamic* state: the fields that change as the simulation steps. It does not capture the scene's *structure*: the entities, their morphs, the solver options, or the number of environments. That structure is fixed by how you build the scene, and restoring a snapshot assumes it is already in place.

- **`SimState`:** the object returned by `scene.get_state()`. It holds one per-solver state object for each active solver, batched over environments.
- **Dynamic state:** positions, velocities, and the internal fields each solver integrates. This is what a checkpoint saves and restores.
- **Static structure:** entities, morphs, geometry, and solver configuration. Not saved. You must reconstruct it before restoring, and it must match.

Because structure is not part of the snapshot, a checkpoint is only valid for a scene built the same way. Restoring into a scene with different entities or solver options is undefined.

## Snapshot and restore in memory

`scene.get_state()` reads the current state into a `SimState`. `scene.reset()` returns the scene to a stored initial state, and `scene.reset(state=...)` restores an arbitrary snapshot:

```python
scene.build()

for _ in range(100):
    scene.step()

state = scene.get_state()  # snapshot the state at step 100

for _ in range(50):
    scene.step()

scene.reset(state=state)  # rewind to the snapshot; the sim continues from step 100
```

:::{warning}
Passing `state` to `reset()` also registers it as the scene's initial state. A subsequent bare `scene.reset()` returns to *this* snapshot, not to the state the scene had at build time. Keep a separate reference to your build-time state if you need both.
:::

The per-solver state objects are plain attribute holders. For the rigid solver, for example, the state carries `qpos`, `dofs_vel`, `links_pos`, and `links_quat`; reading one field looks like this:

```python
state = scene.get_state()
rigid_state = state.solvers_state[scene.solvers.index(scene.rigid_solver)]
qpos = rigid_state.qpos  # shape ([n_envs,] n_qs)
```

The differentiable example [`examples/differentiable_push.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/differentiable_push.py) uses this pattern: it calls `scene.reset()` to restart each optimization pass from a fixed initial state, and reads `scene.get_state().solvers_state[...]` to compute a loss from particle positions mid-rollout.

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

- **`envs_idx`:** the environments to reset, as any array-like of indices. `None` (the default) resets all of them.
- **Partial reset:** with `envs_idx`, only the selected environments take the new state; the others advance uninterrupted.

`envs_idx` applies only to a scene built with environments. On a non-parallelized scene it raises.

## Saving to disk

`save_checkpoint` writes the full physics state (the scene's own fields plus every active solver's fields) to a single pickle file. Restoring requires a scene that was built the same way:

```python
# Process A: run and save.
scene.build()
for _ in range(100):
    scene.step()
scene.save_checkpoint("run.pkl")
```

```python
# Process B: rebuild the same scene, then restore.
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))
scene.build()

scene.load_checkpoint("run.pkl")  # restores state and scene.t
```

`load_checkpoint` also restores `scene.t`, the simulation step count, so a resumed run reports the correct step index.

## What a checkpoint contains

The dynamic state each solver contributes to a snapshot:

| Solver | State fields |
|---|---|
| Rigid | `qpos`, `dofs_vel`, `dofs_acc`, `links_pos`, `links_quat` |
| MPM | `pos`, `vel`, `C`, `F`, `Jp`, `active` |
| SPH | `pos`, `vel`, `active` |
| PBD | `pos`, `vel`, `free` |
| FEM | `pos`, `vel`, `active` |

On disk, a checkpoint is a pickled dictionary. The `arrays` entry is a flat map from a `"Class.field"` key to the raw NumPy array of that field:

```python
{
    "timestamp": ...,   # time.time() at save
    "step_index": ...,  # scene.t at save
    "arrays": {
        "RigidSolver.qpos": ...,
        "MPMSolver.pos": ...,
        # ... one entry per solver field ...
    },
}
```

## Reproducibility notes

- **Configuration must match.** A checkpoint restores fields by name into an already-built scene. The entities, solver options, and environment count must match the scene that produced it. There is no compatibility check: a mismatch fails or silently corrupts state.
- **Precision limits exactness.** Genesis World uses 32-bit floats by default (see {doc}`Hello, Genesis World </user_guide/getting_started/hello_genesis>`). A save/load round trip is therefore accurate to roughly single-precision, not bit-exact. Build with `precision="64"` if you need tighter reproducibility.
- **Serialize before pickling a `SimState`.** A `SimState` returned by `get_state()` holds live references back into the scene and its autograd graph. Call `state.serializable()` first to detach the tensors and drop those references, then pickle it yourself. `save_checkpoint` handles this for you.

```python
state = scene.get_state()
state.serializable()  # detach tensors; safe to pickle

import pickle
with open("state.pkl", "wb") as f:
    pickle.dump(state, f)
```

## See also

- {doc}`Parallel simulation </user_guide/getting_started/parallel_simulation>`: how state is batched over environments.
- {doc}`Scene API </api_reference/scene/scene>`: the full signatures of `get_state`, `reset`, `save_checkpoint`, and `load_checkpoint`.
</content>
</invoke>
