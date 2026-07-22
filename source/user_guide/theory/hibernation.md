# Hibernation

Hibernation puts rigid bodies that have come to rest to sleep, so the solver skips them until something disturbs them. In a scene with a lot of settled geometry, a pile of debris, dropped clutter, a warehouse of parked objects, per-step cost then scales with the number of *awake* bodies rather than the total.

Hibernation builds on **contact islands**: the rigid solver partitions each step into independent groups of interacting bodies and solves them separately. Islands are enabled by default (`use_contact_island=True`). Hibernation extends that partition in time: once an entire island stays below a velocity threshold for a few consecutive steps, the solver stops integrating it until a new contact or applied force wakes it.

## Enabling hibernation

Hibernation is a rigid-solver option, off by default. Turn it on through `gs.options.RigidOptions`:

```python
import genesis as gs

gs.init(backend=gs.cpu, performance_mode=True)

scene = gs.Scene(
    rigid_options=gs.options.RigidOptions(
        use_hibernation=True,
    ),
)
scene.add_entity(gs.morphs.Plane())
scene.add_entity(gs.morphs.Box(pos=(0, 0, 1), size=(0.2, 0.2, 0.2)))

scene.build()
for _ in range(1000):
    scene.step()
```

There are no `hibernate()` or `wake()` calls: hibernation is automatic once enabled. A body becomes eligible to sleep when its speed stays below `hibernation_thresh_vel` for a few consecutive steps, and a whole island sleeps once all of its bodies are ready.

- **`use_hibernation`** (default `False`): the master switch.
- **`hibernation_thresh_vel`** (default `None`): the speed below which a body may sleep, in m/s. Each rotational degree of freedom is weighted by the body's swept radius, so this single linear tolerance covers translation and rotation. Leaving it `None` resolves to `1e-4` under MuJoCo compatibility and `2e-3` otherwise.

:::{note}
The speedup is largest on the CPU backend, where skipping sleeping islands directly raises the serial step rate, and it pairs naturally with `performance_mode=True`. Hibernation has no effect on bodies that are differentiable, prunable, or under no-slip friction, and it is unavailable in differentiable scenes (`requires_grad=True`), which fall back to a dense whole-scene solve.
:::

## Checking what is asleep

Each rigid link exposes whether it is currently hibernated through the solver state. Count the awake bodies to watch a scene settle:

```python
import genesis as gs
from genesis.utils.misc import qd_to_numpy

# ... build and step the scene as above ...

is_hibernated = qd_to_numpy(scene.rigid_solver.links_state.is_hibernated, transpose=True)
n_awake = is_hibernated.size - is_hibernated.sum()  # links not asleep
```

As bodies settle, `n_awake` drops and the step rate climbs.

## See also

- The runnable example [`examples/rigid/hibernation.py`](https://github.com/Genesis-Embodied-AI/genesis-world/blob/main/examples/rigid/hibernation.py) drops a grid of objects and plots the step rate against the awake-body count as they settle.
- {doc}`/user_guide/theory/solvers_and_coupling`: how the rigid solver partitions and integrates the scene.
- {doc}`/user_guide/developers/profiling`: measuring simulation throughput.
- {doc}`/api_reference/engine/solvers/rigid_solver`: the full `RigidOptions` reference.
