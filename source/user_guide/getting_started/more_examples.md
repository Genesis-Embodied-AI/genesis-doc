# More examples

The tutorials in this guide teach one idea at a time. The repository also ships a large tree of runnable example scripts that show those ideas combined into real scenes: the best reference for practical, end-to-end usage. Browse it at [`examples/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples) and run anything that looks close to what you are building.

Every example is a self-contained script you can run directly. The directories group them by topic:

- [`tutorials/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/tutorials): the scripts behind this guide: first scene, visualization, control, parallel simulation, IK, and the soft-body and hybrid-robot walkthroughs.
- [`rigid/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/rigid): the broadest set: rigid-body control, grasping, inverse kinematics, domain randomization, terrain, multi-GPU, and collision-geometry handling.
- [`sensors/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/sensors): IMU, contact and tactile, joint torque, LiDAR, depth camera, surface distance, and temperature sensing.
- [`deformable/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/deformable): FEM and PBD soft bodies on their own: an elastic mesh, a vertex-constraint scene, a liquid, and a differentiable rollout.
- [`fluid/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/fluid): grid-based smoke driven by jets.
- [`coupling/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/coupling), [`sap_coupling/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/sap_coupling), and [`ipc/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/ipc): two-way coupling between rigid bodies, cloth, fluids, and deformables, including the SAP and IPC contact solvers.
- [`collision/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/collision): contact-heavy stacks that stress collision detection, and per-geometry contact filtering.
- [`kinematic/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/kinematic): a kinematic entity showing the commanded pose next to the dynamic robot tracking it.
- [`rendering/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/rendering): rendering modes, moving and entity-following cameras, and render performance.
- [`drone/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/drone): quadrotor flight, a PID controller, keyboard teleoperation, and a reinforcement-learning hover task.
- [`locomotion/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/locomotion) and [`manipulation/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/manipulation): full RL pipelines (Go2 walking, Franka grasping) plus a behavior-cloning example.
- [`usd/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/usd): importing USD stages and larger authored scenes.
- [`viewer_plugin/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/viewer_plugin): extending the interactive viewer with mouse interaction and mesh picking.
- [`gui/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/gui): an ImGui overlay with playback controls, joint sliders, an entity browser, and custom panels.
- [`speed_benchmark/`](https://github.com/Genesis-Embodied-AI/genesis-world/tree/main/examples/speed_benchmark): throughput benchmarks.