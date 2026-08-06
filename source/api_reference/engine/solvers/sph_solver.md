# SPHSolver

The `SPHSolver` implements Smoothed Particle Hydrodynamics for liquid simulation. It approximates fluid dynamics with particles, deriving pressure forces from local density, viscosity forces from velocity differences, and surface tension, with free-surface handling. Pick the pressure solver with `pressure_solver`: weakly compressible SPH (`"WCSPH"`) or divergence-free SPH (`"DFSPH"`). It simulates the `SPH.Liquid` material; see {doc}`/api_reference/engine/material/sph`. For usage, see {doc}`/user_guide/physics/beyond_rigid_bodies`.

## Options

```{eval-rst}
.. autoclass:: genesis.options.solvers.SPHOptions
```

## SPHSolver

```{eval-rst}
.. autoclass:: genesis.engine.solvers.sph_solver.SPHSolver
    :members:
    :undoc-members:
    :show-inheritance:
```

## See also

- {doc}`/api_reference/engine/entity/sph_entity`: SPHEntity.
- {doc}`/api_reference/engine/material/sph`: SPH materials.
