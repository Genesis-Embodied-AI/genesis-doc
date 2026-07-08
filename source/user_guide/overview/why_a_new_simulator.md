# Why a new simulator

Genesis World was built to remove the friction that has kept physics simulation hard to adopt in robotics research: opaque internals, heavy APIs, and complex software stacks. It differs from prior platforms in a few deliberate ways.

- **Pythonic and transparent.** Genesis World is open source and implemented in Python, so its behavior is easy to read, debug, and extend.
- **Simple to install and use.** A single `pip install` sets it up, and the API is designed to stay small and predictable as scenes grow.
- **Fast parallel simulation.** Genesis World runs many environments in parallel on a single GPU — up to 10–80× faster than prior GPU-accelerated simulators such as Isaac Gym/Sim/Lab and MuJoCo MJX, without compromising accuracy. See the [blog post](https://www.genesis.ai/blog/the-role-of-simulation-in-scalable-robotics-genesis-world-10-and-the-path-forward) for methodology.
- **Unified multi-physics.** A single framework integrates rigid, FEM, MPM, and particle solvers over a shared scene and state, with strong coupling to [uipc](https://github.com/spiriMirror/libuipc) for more accurate FEM simulation.
- **Photorealistic rendering.** [Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx), an in-house renderer built for robotics, produces ray-traced images with performance tuned for simulation workloads.
- **Differentiable.** Genesis World is compatible with differentiable simulation; autodiff and backpropagation are provided through the [Quadrants](https://github.com/Genesis-Embodied-AI/quadrants) compiler, with hand-derived gradients for some complex kernels.
- **Comprehensive sensors.** Physically accurate, differentiable tactile sensors sit alongside IMU, lidar, depth-camera, contact-force, surface-distance, and temperature-grid sensors — all usable out of the box in parallel and heterogeneous environments. Camera-based rendering (Nyx, Luisa, Pyrender) is exposed through the same sensor interface.
