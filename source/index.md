# Genesis World

![Genesis World teaser: simulated robots and environments rendered in Genesis World](_static/images/genesis_world_teaser.png)

[![GitHub Repo stars](https://img.shields.io/github/stars/Genesis-Embodied-AI/genesis-world?style=plastic&logo=GitHub&logoSize=auto)](https://github.com/Genesis-Embodied-AI/genesis-world)
[![PyPI version](https://badge.fury.io/py/genesis-world.svg?icon=si%3Apython)](https://pypi.org/project/genesis-world/)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgenesis-embodied-ai.github.io%2F)](https://genesis-embodied-ai.github.io/)

**Genesis World** is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photorealistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a single Pythonic API. It scales from a laptop CPU to datacenter GPUs, and it is written in Python so you can read, extend, and embed it directly in research code.

Genesis World began as an academic project in December 2024, under the name **Genesis**, and is now developed with support from [Genesis AI](https://www.genesis.ai/). For a tour of how the system fits together, see {doc}`/user_guide/overview/what_is_genesis`; for the design rationale, see the [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward).

## Getting started

Install PyTorch by following the [official instructions](https://pytorch.org/get-started/locally/), then install Genesis World from PyPI:

```bash
pip install genesis-world
```

From there, the {doc}`user guide </user_guide/index>` covers installation in detail, tutorials, and the full API reference.

## Contributing

Genesis World aims to be a transparent, community-driven ecosystem where roboticists and graphics researchers build a fast, physically and visually realistic virtual world together. Contributions of every size are welcome: pull requests for new features, bug reports, and suggestions that make the API more intuitive. See the {doc}`introduction </user_guide/overview/what_is_genesis>` for the longer story.

## Support

- Report bugs and request features through GitHub [Issues](https://github.com/Genesis-Embodied-AI/genesis-world/issues).
- Ask questions and share ideas in GitHub [Discussions](https://github.com/Genesis-Embodied-AI/genesis-world/discussions).

## Citation

If Genesis World supports your research, please cite it. A technical report is in progress; until it is published, you can cite:

```bibtex
@misc{Genesis,
  author = {Genesis Authors},
  title  = {Genesis: A Generative and Universal Physics Engine for Robotics and Beyond},
  month  = {December},
  year   = {2024},
  url    = {https://github.com/Genesis-Embodied-AI/genesis-world}
}
```

```{toctree}
:maxdepth: 1

user_guide/index
api_reference/index
```
