# Overview

Genesis World is a simulation platform for physical AI development. It combines a unified multi-physics engine, a photorealistic renderer ([Nyx](https://github.com/Genesis-Embodied-AI/genesis-nyx)), and a cross-platform compiler ([Quadrants](https://github.com/Genesis-Embodied-AI/quadrants)) behind a single Pythonic API, and it scales from a laptop CPU to datacenter GPUs without a change to your code.

This section is the orientation for everything that follows. Read it first to understand what the platform is and where it came from, then install it so the {doc}`Getting Started </user_guide/getting_started/index>` tutorials have something to run against. It carries no simulation code of its own; the hands-on material begins in the next section.

- {doc}`what_is_genesis` explains the design in one place: the multi-physics engine, the rendering and compilation stack, and the project's history from an academic release to its current development. Read it for the mental model and the vocabulary the rest of the guide assumes.
- {doc}`installation` covers installing on Linux, macOS, and Windows, on CPU and on CUDA and non-CUDA GPUs, along with the optional renderers and the choices (backend, precision) you make once at install time.

```{toctree}
:hidden:
:maxdepth: 1

what_is_genesis
installation
```
