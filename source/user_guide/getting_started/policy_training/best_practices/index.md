# 🧭 Best Practices

Patterns and tooling for writing RL training pipelines that scale on Genesis.

- [**Writing an Efficient RL Environment**](efficient_environment) - pre-allocated buffers, boolean-mask `envs_idx`, zero-copy state accessors, efficient robot reset and command application, errno-based termination.
- [**Domain Randomization**](domain_randomization) - randomizing physics parameters across environments to train policies that generalize.

```{toctree}
:hidden:
:maxdepth: 1

efficient_environment
domain_randomization
```
