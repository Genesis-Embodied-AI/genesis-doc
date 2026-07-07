# Genesis World

![Genesis World teaser](https://raw.githubusercontent.com/YilingQiao/Genesis/readme-assets/videos/HeroShot_Final.png)

[![GitHub Repo stars](https://img.shields.io/github/stars/Genesis-Embodied-AI/Genesis?style=plastic&logo=GitHub&logoSize=auto)](https://github.com/Genesis-Embodied-AI/Genesis)
[![PyPI version](https://badge.fury.io/py/genesis-world.svg?icon=si%3Apython)](https://pypi.org/project/genesis-world/)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgenesis-embodied-ai.github.io%2F)](https://genesis-embodied-ai.github.io/)
[![Discord](https://img.shields.io/discord/1322086972302430269?logo=discord)](https://discord.gg/nukCuhB47p)
<a href="https://drive.google.com/uc?export=view&id=1ZS9nnbQ-t1IwkzJlENBYqYIIOOZhXuBZ"><img src="https://img.shields.io/badge/WeChat-07C160?style=for-the-badge&logo=wechat&logoColor=white" height="20" style="display:inline"></a>


## What is Genesis World?

**Genesis World** is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photo-realistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a Pythonic simulation interface. Genesis World is designed to scale from a single laptop kernel to datacenter-grade GPUs, while remaining easy to read, extend, and embed in research code.

It was previously named **Genesis** and started as an academic project in Dec 2024; its development is now officially supported by [Genesis AI](https://www.genesis.ai/). For more technical details, see our [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward).

Genesis World occupies four layers. Above sits whatever you build (robotics environments, ML pipelines, agentic simulation); below sits whatever compute backend you have.

- **Simulation Interface** — the user-facing API: asset parsing (URDF, MJCF, OBJ, GLB, USD, …), entity accessors, controllers, sensors, parallel and heterogeneous environments, and a built-in GUI.
- **Physics** — a unified multi-physics engine integrating Rigid, FEM, MPM, Particle (PBD / SPH), [uipc](https://github.com/spiriMirror/libuipc), an explicit coupler, and SAP, all sharing one scene and one state.
- **Render** — three rendering paths plug in as camera sensors: **[Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)** (our in-house renderer designed for robotics), **Luisa** (DSL ray tracer), and **Pyrender** (rasterizer).
- **Compiler** — **[Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)** lowers Python kernel code to CUDA, AMD ROCm, Apple Metal, Vulkan, x86, and ARM64. It carries Genesis World's autodiff, GPU graphs, and fastcache machinery.

## Key Features

Compared to prior simulation platforms, here we highlight several key features of Genesis World:

- 🐍 **Pythonic** and fully transparent. Genesis World is developed and fully open-source in Python, making code understanding and contribution way easier.
- 👶 **Effortless installation** and **extremely simple** and **user-friendly** API design.
- 🚀 **Parallelized simulation** with ***unprecedented speed***: Genesis World is the **world's fastest physics engine**, delivering simulation speeds up to ***10~80x*** (yes, this is a bit sci-fi) faster than existing *GPU-accelerated* robotic simulators (Isaac Gym/Sim/Lab, Mujoco MJX, etc.), ***without any compromise*** on simulation accuracy and fidelity.
- 💥 A **unified** framework that supports various state-of-the-art physics solvers, modeling **a vast range of materials** and physical phenomena.
- 📸 Photo-realistic ray-tracing rendering via [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx), with optimized performance for robotics applications.
- 📐 **Differentiability**: Genesis World is designed to be fully compatible with differentiable simulation, with autodiff and backpropagation infrastructure provided by [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants).
- ☝🏻 A **comprehensive sensor system** built into the simulation interface: physically-accurate and differentiable **tactile** sensors alongside **IMU**, **lidar**, **depth camera**, **contact force**, **surface distance**, and **temperature grid** sensors — all usable out of the box with parallel and heterogeneous environments.

## Getting Started

### Quick Installation

Genesis World is available via PyPI:

```bash
pip install genesis-world
```

You also need to install **PyTorch** following the [official instructions](https://pytorch.org/get-started/locally/).

### Documentation

Please refer to our [documentation site](https://genesis-world.readthedocs.io/en/latest/user_guide/index.html) to for detailed installation steps, tutorials and API references.

## Contributing to Genesis World

The goal of the Genesis project is to build a fully transparent, user-friendly ecosystem where contributors from both robotics and computer graphics can **come together to collaboratively create a high-efficiency, realistic (both physically and visually) virtual world for robotics research and beyond**.

We sincerely welcome *any forms of contributions* from the community to make the world a better place for robots. From **pull requests** for new features, **bug reports**, to even tiny **suggestions** that will make Genesis World API more intuitive, all are wholeheartedly appreciated!

## Support

- Please use Github [Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues) for bug reports and feature requests.

- Please use GitHub [Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions) for discussing ideas, and asking questions.

## Citation

If you used Genesis World in your research, we would appreciate it if you could cite it. We are still working on a technical report, and before it's public, you could consider citing:

```
@misc{Genesis,
  author = {Genesis Authors},
  title = {Genesis: A Generative and Universal Physics Engine for Robotics and Beyond},
  month = {December},
  year = {2024},
  url = {https://github.com/Genesis-Embodied-AI/Genesis}
}
```

```{toctree}
:maxdepth: 1

user_guide/index
api_reference/index

```
