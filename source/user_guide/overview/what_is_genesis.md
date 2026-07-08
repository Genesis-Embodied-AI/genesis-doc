# Introduction

![Genesis World teaser: simulated robots and environments rendered in Genesis World](../../_static/images/genesis_world_teaser.png)

**Genesis World** is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photorealistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a single Pythonic API. It scales from a laptop CPU to datacenter GPUs while staying readable and easy to embed in research code.

Genesis World began as an academic project in December 2024, under the name **Genesis**, and is now developed with support from [Genesis AI](https://www.genesis.ai/). For the design rationale, see the [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward).

## The stack

Genesis World occupies four layers. Above it sits whatever you build — robotics environments, ML pipelines, agentic simulation. Below it sits whatever compute backend you have.

- **Simulation interface** — the user-facing API: asset parsing (URDF, MJCF, OBJ, GLB, USD, …), entity accessors, controllers, sensors, parallel and heterogeneous environments, and a built-in viewer.
- **Physics** — a unified multi-physics engine integrating rigid, FEM, MPM, and particle (PBD/SPH) solvers, [uipc](https://github.com/spiriMirror/libuipc), an explicit coupler, and SAP, all sharing one scene and one state.
- **Render** — three rendering paths plug in as camera sensors: [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx), an in-house renderer built for robotics; Luisa, a DSL ray tracer; and Pyrender, a rasterizer.
- **Compiler** — [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) lowers Python kernel code to CUDA, AMD ROCm, Apple Metal, Vulkan, x86, and ARM64. It carries the autodiff, GPU-graph, and fast-cache machinery.

## Philosophy

Genesis World is shaped by a few convictions about what a simulator for physical AI should be.

- **Transparent and Pythonic.** The engine is open source and written in Python, so you can read it, debug it, and extend it — no opaque binary between you and the physics.
- **Unified, not bolted together.** Rigid, FEM, MPM, and particle (PBD/SPH) solvers share one scene and one state with explicit coupling, rather than living in separate tools you have to stitch together.
- **Fast without cutting corners.** Simulation is parallelized across environments on the GPU — up to 10–80× faster than prior GPU-accelerated simulators such as Isaac Gym/Sim/Lab and MuJoCo MJX — without trading away accuracy. See the [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward) for methodology.
- **Differentiable by design.** Autodiff and backpropagation run through the [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) compiler, with hand-derived gradients for the hardest kernels, so gradients flow through the physics.
- **Perception built in.** Physically accurate, differentiable tactile sensors sit alongside IMU, lidar, depth-camera, contact-force, surface-distance, and temperature-grid sensors — and all three renderers are exposed through the same camera-sensor interface — usable out of the box in parallel and heterogeneous environments.
- **Easy to start, easy to scale.** A single `pip install`, a small API, and the same code path from one environment on a laptop to thousands on a datacenter GPU.

## Mission

Simulation trains policies, generates data, and turns computation into capability. Yet researchers have long been held back by simulators that are hard to learn or closed off — intricate data-centric abstractions, heavy APIs, and physics you cannot inspect or adapt to what you observe in the real world.

Genesis World exists to change that: a transparent, welcoming platform where researchers from physics simulation and robotics build a fast, physically and visually realistic virtual world together, and where the computer-graphics community's advances in simulation and rendering reach robotics instead of staying out of reach. It is early, and a small team will not get everything right on a first release — so contributions of every kind are welcome. Open an issue or a pull request on [GitHub](https://github.com/Genesis-Embodied-AI/genesis-world); we would love to hear from you.
