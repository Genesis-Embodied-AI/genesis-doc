# `LegacyCoupler`

The `LegacyCoupler` is the default coupler. It handles every cross-solver pair (rigid, MPM, SPH, PBD, FEM) and is the right choice for general multi-physics scenes. It is slated for deprecation in favor of the SAP and IPC couplers. The scene uses it when you pass no `coupler_options`.

## Minimal example

```python
import genesis as gs

gs.init()
scene = gs.Scene()  # LegacyCoupler is selected by default
```

To disable coupling for a specific pair of solvers, pass `gs.options.LegacyCouplerOptions` with that pair set to `False`:

```python
scene = gs.Scene(
    coupler_options=gs.options.LegacyCouplerOptions(
        rigid_mpm=True,   # rigid <-> MPM coupling (default True)
        rigid_sph=False,  # disable rigid <-> SPH coupling
    ),
)
```

## Configuration

Each field of `LegacyCouplerOptions` is a boolean that enables one solver pair (`rigid_mpm`, `rigid_sph`, `rigid_pbd`, `rigid_fem`, `mpm_sph`, `mpm_pbd`, `fem_mpm`, `fem_sph`), all `True` by default. See {doc}`/api_reference/options/simulator_coupler_and_solver_options/legacy_coupler_options` for the full list.

## See also

- {doc}`index`: coupler overview and how to choose one.
- {doc}`/user_guide/theory/couplers/index`: the theory behind each coupler.
- {doc}`/api_reference/options/simulator_coupler_and_solver_options/legacy_coupler_options`: legacy coupler options.
