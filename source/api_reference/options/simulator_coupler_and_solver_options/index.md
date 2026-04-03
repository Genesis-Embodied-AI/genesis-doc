# Simulator, Coupler & Solver Options

This configures the global simulator, all the solvers inside it, and the inter-solver coupler.

:::{note}
`SimOptions` specifies the global settings for the simulator. Some parameters exist both in `SimOptions` and `SolverOptions`. In this case, if such parameters are given in `SolverOptions`, it will override the one specified in `SimOptions` for this specific solver. For example, if `dt` is only given in `SimOptions`, it will be shared by all the solvers, but it's also possible to let a solver run at a different temporal speed by setting its own `dt` to be a different value.
:::

```{toctree}
:maxdepth: 2

sim_options
coupler_options
tool_options
rigid_options
mpm_options
sph_options
pbd_options
fem_options
sf_options
```
