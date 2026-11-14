# States

A state holds the runtime data of a simulation: positions, velocities, forces, and the solver-specific variables that evolve each step. `scene.get_state()` returns a `SimState`, an aggregate snapshot of the whole scene that holds a `SolverCheckpoint` for each active solver. In practice, read state through the entity or solver getters and restore snapshots with `scene.reset(state=...)`; see {doc}`/user_guide/configuration/checkpoints` and {doc}`/user_guide/configuration/conventions`.

## Simulation state

```{eval-rst}
.. autoclass:: genesis.engine.states.solvers.SimState
    :members:
    :undoc-members:
    :show-inheritance:
```

## Per-solver states

```{eval-rst}
.. autoclass:: genesis.engine.states.solvers.SolverCheckpoint
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/configuration/checkpoints`: saving and restoring simulation state.
- {doc}`/user_guide/configuration/conventions`: tensor shape and dtype conventions.
- {doc}`/user_guide/configuration/differentiable_simulation`: gradient-tracking state in differentiable simulation.
