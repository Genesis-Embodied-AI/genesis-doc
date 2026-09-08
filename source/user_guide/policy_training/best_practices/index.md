# Best practices

Reinforcement learning in Genesis World runs thousands of environments in parallel on a single GPU. At that scale, training depends on an efficient step loop, valid simulation states, and enough variation for the policy to transfer beyond the conditions it saw. Environment code sits on the critical path, so every host-device transfer, every buffer re-allocation, and every Python-side branch inside the step loop costs throughput that no amount of GPU compute wins back.

- **{doc}`efficient_environment`:** keep `env.step()` free of GPU synchronization with pre-allocated buffers, boolean-mask `envs_idx`, and zero-copy state accessors.
- **{doc}`simulation_stability`:** diagnose rigid solver errors and recover episodes affected by numerical divergence.
- **{doc}`domain_randomization`:** randomize physics and visual properties across environments so the trained policy generalizes rather than overfitting to one configuration.

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
simulation_stability
domain_randomization
```
