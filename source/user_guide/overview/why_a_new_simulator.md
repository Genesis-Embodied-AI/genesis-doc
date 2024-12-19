# 🧬 Why A New Physics Simulator
Compared to prior simulation platforms, here we highlight several key features of Genesis:
- 🐍 **Pythonic** and fully transparent. Genesis is developed and fully open-source in python, making code understanding and contribution way more easier.
- 👶 **Effortless installation** and **extremely simple** and **user-friendly** API design.
- 🚀 **Parallelized simulation** with ***unprecedented speed***: Genesis is the **world's fastest physics engine**, delivering simulation speeds up to ***10~80x*** (yes, this is a bit sci-fi) faster than existing *GPU-accelerated* robotic simulators (Isaac Gym/Sim/Lab, Mujoco MJX, etc), ***without any compromise*** on simulation accuracy and fidelity.
- 💥 A **unified** framework that supports various state-of-the-art physics solvers, modeling **a vast range of materials** and physical phenomena.
- 📸 Photo-realistic ray-tracing rendering with optimized performance.
- 📐 **Differentiability**: Genesis is designed to be fully compatible with differentiable simulation. Currently, our MPM solver and Tool Solver are differentiable, and differentiability for other solvers will be added soon (starting with rigid-body simulation).
- ☝🏻 Physically-accurate and differentiable **tactile sensor**.
- 🌌 Native support for ***[Generative Simulation](https://arxiv.org/abs/2305.10455)***, allowing **language-prompted data generation** of various modalities: *interactive scenes*, *task proposals*, *rewards*, *assets*, *character motions*, *policies*, *trajectories*, *camera motions*, *(physically-accurate) videos*, and more.

