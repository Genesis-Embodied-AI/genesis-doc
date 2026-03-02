# 💾 Checkpoints

Genesis provides state save/load functionality for training resumption and episode resets.

## Basic Save/Load

```python
import genesis as gs

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene.build()

# Simulate
for _ in range(100):
    scene.step()

# Save checkpoint
scene.save_checkpoint("checkpoint.pkl")

# Load in new scene
scene2 = gs.Scene()
robot2 = scene2.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene2.build()
scene2.load_checkpoint("checkpoint.pkl")
```

## State Objects

```python
# Get current state (in-memory)
state = scene.get_state()

# Reset to initial state
scene.reset()

# Reset to custom state
scene.reset(state=state)
```

## RL Episode Resets

```python
scene.build(n_envs=N)

# Snapshot initial state
init_state = scene.get_state()

for episode in range(num_episodes):
    scene.reset(state=init_state)

    for step in range(episode_length):
        scene.step()
        obs, reward, done = get_observations()

        # Reset environments where episode ended
        if done.any():
            done_envs = torch.where(done)[0].tolist()
            scene.reset(state=init_state, envs_idx=done_envs)
```

## Selective Environment Reset

```python
scene.build(n_envs=16)

# Reset all environments
scene.reset()

# Reset specific environments
scene.reset(envs_idx=[0, 2, 5])

# Reset with custom state for specific envs
scene.reset(state=init_state, envs_idx=[1, 3, 7])
```

## State Contents

The `SimState` object contains:

| Solver | State Variables |
|--------|-----------------|
| Rigid | `qpos`, `dofs_vel`, `links_pos`, `links_quat` |
| MPM | `pos`, `vel`, `C`, `F`, `Jp`, `active` |
| SPH | `pos`, `vel`, `active` |
| PBD | `pos`, `vel`, `free` |
| FEM | `pos`, `vel`, `active` |

## Checkpoint File Format

Checkpoints are pickled dictionaries:

```python
{
    "timestamp": time.time(),
    "step_index": scene.t,
    "arrays": {  # Numpy arrays keyed by solver/field
        "RigidSolver.qpos": np.array(...),
        "MPMSolver.pos": np.array(...),
        ...
    }
}
```

## Serialization for Transfer

```python
# Make state serializable (detach from graph)
state = scene.get_state()
state_serializable = state.serializable()

# Now safe to pickle
import pickle
with open("state.pkl", "wb") as f:
    pickle.dump(state_serializable, f)
```

## Important Notes

- Checkpoints require compatible scene configuration (same entities, solver options)
- 32-bit precision may lose ~2e-6 accuracy between save/load
- Use `envs_idx` parameter for efficient partial resets
- `scene.t` stores the simulation step count
