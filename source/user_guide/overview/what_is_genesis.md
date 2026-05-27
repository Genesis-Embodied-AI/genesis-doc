# 🌱 What is Genesis World

![Genesis World teaser](https://raw.githubusercontent.com/YilingQiao/Genesis/readme-assets/videos/HeroShot_Final.png)

**Genesis World** is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photo-realistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/nyx-for-genesis)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a Pythonic simulation interface. Genesis World is designed to scale from a single laptop kernel to datacenter-grade GPUs, while remaining easy to read, extend, and embed in research code.

It was previously named **Genesis** and started as an academic project in Dec 2024; its development is now officially supported by [Genesis AI](https://www.genesis.ai/). For more technical details, see our [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward).

## The stack

Genesis World occupies four layers. Above sits whatever you build (robotics environments, ML pipelines, agentic simulation); below sits whatever compute backend you have.

- **Simulation Interface** — the user-facing API: asset parsing (URDF, MJCF, OBJ, GLB, USD, …), entity accessors, controllers, sensors, parallel and heterogeneous environments, and a built-in GUI.
- **Physics** — a unified multi-physics engine integrating Rigid, FEM, MPM, Particle (PBD / SPH), [uipc](https://github.com/spiriMirror/libuipc), an explicit coupler, and SAP, all sharing one scene and one state.
- **Render** — three rendering paths plug in as camera sensors: **[Nyx](https://github.com/Genesis-Embodied-AI/nyx-for-genesis)** (our in-house renderer designed for robotics), **Luisa** (DSL ray tracer), and **Pyrender** (rasterizer).
- **Compiler** — **[Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)** lowers Python kernel code to CUDA, AMD ROCm, Apple Metal, Vulkan, x86, and ARM64. It carries Genesis World's autodiff, GPU graphs, and fastcache machinery.

## Long-term missions

Genesis World is built and will continuously evolve with the following ***long-term missions***:

1. **Lowering the barrier** to using physics simulations and making robotics research accessible to everyone. (See our [commitment](https://genesis-world.readthedocs.io/en/latest/user_guide/overview/mission.html).)
2. **Unifying a wide spectrum of state-of-the-art physics solvers** into a single framework, allowing re-creating the whole physical world in a virtual realm with the highest possible physical, visual, and sensory fidelity, using the most advanced simulation techniques.
3. **Building a sensor-first simulation interface** so cameras, depth, IMU, lidar, tactile, contact, and other modalities live behind one consistent API across all rendering and physics backends.
