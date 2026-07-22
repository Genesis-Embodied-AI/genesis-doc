# States

A state holds the runtime data of a simulation: positions, velocities, forces, and the solver-specific variables that evolve each step. `scene.get_state()` returns a `SimState`, an aggregate snapshot of the whole scene that holds one per-solver state for each active solver. In practice you read state through the entity or solver getters and restore snapshots with `scene.reset(state=...)`; see {doc}`/user_guide/configuration/checkpoints` and {doc}`/user_guide/configuration/conventions`.

## Simulation state

```{eval-rst}
.. autoclass:: genesis.engine.states.solvers.SimState
    :members:
    :undoc-members:
    :show-inheritance:
```

## Per-solver states

```{eval-rst}
.. autoclass:: genesis.engine.states.solvers.RigidSolverState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.solvers.MPMSolverState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.solvers.FEMSolverState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.solvers.PBDSolverState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.solvers.SPHSolverState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.solvers.ToolSolverState
    :members:
    :undoc-members:
    :show-inheritance:
```

## Per-entity states

```{eval-rst}
.. autoclass:: genesis.engine.states.entities.RigidEntityState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.entities.MPMEntityState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.entities.FEMEntityState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.entities.SPHEntityState
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: genesis.engine.states.entities.ToolEntityState
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/user_guide/configuration/checkpoints`: saving and restoring simulation state.
- {doc}`/user_guide/configuration/conventions`: tensor shape and dtype conventions.
- {doc}`/api_reference/differentiation/index`: gradient-tracking state in differentiable simulation.
