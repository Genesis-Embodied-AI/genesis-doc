# 仿真器、耦合器与求解器选项

此部分用于配置全局仿真器、其中的所有求解器以及求解器间的耦合器。

:::{note}
`SimOptions` 指定了仿真器的全局设置。某些参数同时存在于 `SimOptions` 和 `SolverOptions` 中。在这种情况下，如果在 `SolverOptions` 中指定了这些参数，则会覆盖 `SimOptions` 中指定的值，仅对该特定求解器生效。例如，如果仅在 `SimOptions` 中设置了 `dt`，则所有求解器将共享该时间步长；但也可以通过为特定求解器设置不同的 `dt` 值，使其以不同的时间速度运行。
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
