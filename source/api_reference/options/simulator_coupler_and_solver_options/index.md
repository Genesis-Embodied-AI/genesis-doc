# 模拟器、耦合器和求解器选项

此配置用于全局模拟器、其中的所有求解器以及求解器之间的耦合器。

:::{note}
`SimOptions` 指定了模拟器的全局设置。一些参数在 `SimOptions` 和 `SolverOptions` 中都存在。在这种情况下，如果在 `SolverOptions` 中给出了这些参数，它将覆盖在 `SimOptions` 中为该特定求解器指定的参数。例如，如果 `dt` 仅在 `SimOptions` 中给出，它将被所有求解器共享，但也可以通过设置自己的 `dt` 为不同的值来让某个求解器以不同的时间速度运行。
:::

```{toctree}
:maxdepth: 2

sim_options
coupler_options
tool_options
rigid_options
avatar_options
mpm_options
sph_options
pbd_options
fem_options
sf_options
```

