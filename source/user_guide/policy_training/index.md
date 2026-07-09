# Policy Training

Genesis World is built for reinforcement learning at scale: thousands of environments running in parallel on a single GPU, and multiple GPUs beyond that. At that scale the bottleneck is rarely the learning algorithm; it is how efficiently each environment steps and how well the whole pipeline keeps the GPU busy. This section covers both the principles that make large-scale training work and the complete, runnable examples that put them into practice.

Read the best-practices material first to understand what governs throughput and sim-to-real transfer, then study the worked examples as templates for your own tasks, and turn to multi-GPU when one device is no longer enough. It assumes you are comfortable with {doc}`parallel simulation </user_guide/getting_started/parallel_simulation>`, which introduces the batched execution these environments rely on.

- {doc}`best_practices/index` collects what decides whether training succeeds at scale: writing an environment whose `step()` does not stall the GPU, and randomizing the simulation so a policy transfers to hardware.
- {doc}`examples/index` walks through the end-to-end RL pipelines that ship with Genesis World, drone hover, quadruped locomotion, and two-stage manipulation, each a gym-style environment plus a training script you can run as-is.
- {doc}`multi_gpu` covers scaling training across several GPUs, the second axis of parallelism beyond the batched environments within one device.

```{toctree}
:hidden:
:maxdepth: 2

best_practices/index
examples/index
multi_gpu
```
