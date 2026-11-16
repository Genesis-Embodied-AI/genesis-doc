# Policy Training

Genesis World is built for reinforcement learning at scale: thousands of environments in parallel on one GPU, and multiple GPUs beyond that. At that scale the bottleneck is rarely the learning algorithm but how efficiently each environment steps and how well the pipeline keeps the GPU busy. This section covers the complete RL examples that ship with Genesis World and domain randomization. For keeping the step loop fast and scaling across GPUs, see {doc}`Performance </user_guide/performance/index>`. It assumes you are comfortable with {doc}`parallel simulation </user_guide/getting_started/parallel_simulation>`.

```{toctree}
:hidden:
:maxdepth: 2

domain_randomization
examples/index
```
