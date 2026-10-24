# Performance

Genesis World is fast by default, but a slow scene is usually slow for one of a few reasons: too much data crossing between the CPU and the GPU each step, too few environments to fill the GPU, or one solver stage that dominates the step. This section covers how to find the cause and what to change.

- {doc}`Efficient environments <efficient_environment>`: keep the step loop on the GPU, batch work across environments, and avoid per-step host synchronization.
- {doc}`Profiling <profiling>`: measure where the time goes, from the Python call stack down to individual Quadrants kernels.
- {doc}`Multi-GPU <multi_gpu>`: run one scene per GPU and scale training across devices.

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
profiling
multi_gpu
```
