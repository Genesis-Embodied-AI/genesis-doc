# Best practices

Reinforcement learning in Genesis World runs thousands of environments in parallel on a single GPU. At that scale, two things dominate whether training succeeds: how fast each `env.step()` runs, and whether the policy transfers beyond the exact conditions it saw. Environment code sits on the critical path, so every host-device transfer, every buffer re-allocation, and every Python-side branch inside the step loop costs throughput that no amount of GPU compute wins back.

- **{doc}`efficient_environment`:** keep `env.step()` free of GPU synchronization with pre-allocated buffers, boolean-mask `envs_idx`, and zero-copy state accessors.
- **{doc}`domain_randomization`:** randomize physics and visual properties across environments so the trained policy generalizes rather than overfitting to one configuration.

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
domain_randomization
```
