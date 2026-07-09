# Getting Started

These tutorials teach Genesis World by building working programs, one idea at a time. Together they cover the full arc of a simulation: initialize the engine, describe a scene, build it, step it, control what is in it, and scale it to thousands of parallel copies on the GPU. Work through them in order if you are new; each one assumes the one before it.

Every Genesis World program follows the same shape, and these pages introduce it piece by piece before the rest of the guide goes deep on any single part. By the end you will have loaded and actuated a robot, run batched environments, and know where to find the larger example scripts that combine these ideas into complete tasks.

- {doc}`hello_genesis` is the smallest complete program: load a Franka arm above a ground plane and let it fall. Under fifteen lines, it already contains every step common to any Genesis World simulation.
- {doc}`control_your_robot` actuates that arm with the built-in controllers, introducing the position and force control modes and the joint and DOF indexing you use to command them.
- {doc}`parallel_simulation` runs many copies of a scene at once on the GPU. This batched execution is what makes Genesis World fast enough for reinforcement learning and large-scale data generation.
- {doc}`more_examples` is the map to the repository's runnable example tree, which shows these ideas combined into realistic tasks you can run and adapt.

```{toctree}
:hidden:
:maxdepth: 1

hello_genesis
control_your_robot
parallel_simulation
more_examples
```
