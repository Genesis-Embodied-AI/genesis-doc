# Best practices

Reinforcement learning in Genesis World runs thousands of environments in parallel on a single GPU. At that scale, two things dominate whether training succeeds: how fast each `env.step()` runs, and whether the policy you train transfers beyond the exact conditions it saw. The pages in this section cover the patterns that address both.

Environment code sits on the critical path, so every host-device transfer, every buffer re-allocation, and every Python-side branch inside the step loop costs throughput that no amount of GPU compute wins back. Both pages come down to the same two habits: keep the step loop on the GPU, and vary the physics across environments so the policy sees a distribution rather than a single world.

Start here:

- **Writing an efficient RL environment:** keep `env.step()` free of GPU synchronization with pre-allocated buffers, boolean-mask `envs_idx`, and zero-copy state accessors. See {doc}`efficient_environment`.
- **Domain randomization:** randomize physics and visual properties across environments so the trained policy generalizes rather than overfitting to one configuration. See {doc}`domain_randomization`.

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
domain_randomization
```
