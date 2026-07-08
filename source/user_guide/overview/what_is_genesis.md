# What is Genesis World

![Genesis World teaser: simulated robots and environments rendered in Genesis World](../../_static/images/genesis_world_teaser.png)

**Genesis World** is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photorealistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a single Pythonic API. It scales from a laptop CPU to datacenter GPUs while staying readable and easy to embed in research code.

Genesis World began as an academic project in December 2024, under the name **Genesis**, and is now developed with support from [Genesis AI](https://www.genesis.ai/). For the design rationale, see the [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward).

## The stack

Genesis World occupies four layers. Above it sits whatever you build — robotics environments, ML pipelines, agentic simulation. Below it sits whatever compute backend you have.

- **Simulation interface** — the user-facing API: asset parsing (URDF, MJCF, OBJ, GLB, USD, …), entity accessors, controllers, sensors, parallel and heterogeneous environments, and a built-in viewer.
- **Physics** — a unified multi-physics engine integrating rigid, FEM, MPM, and particle (PBD/SPH) solvers, [uipc](https://github.com/spiriMirror/libuipc), an explicit coupler, and SAP, all sharing one scene and one state.
- **Render** — three rendering paths plug in as camera sensors: [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx), an in-house renderer built for robotics; Luisa, a DSL ray tracer; and Pyrender, a rasterizer.
- **Compiler** — [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) lowers Python kernel code to CUDA, AMD ROCm, Apple Metal, Vulkan, x86, and ARM64. It carries the autodiff, GPU-graph, and fast-cache machinery.
