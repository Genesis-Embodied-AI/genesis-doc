# Genesis

```{figure} _static/images/teaser.png
```

## 什么是Genesis？

Genesis是一个为通用*机器人/具身AI/物理AI*应用设计的物理平台。它同时具备多个功能：

1. 一个从头开始重建的**通用物理引擎**，能够模拟各种材料和物理现象。
2. 一个**轻量级**、**超快**、**Python化**且**用户友好**的机器人仿真平台。
3. 一个强大且快速的**照片级真实感渲染系统**。
4. 一个**生成数据引擎**，可以将用户提示的自然语言描述转换为各种数据模式。

Genesis由一个重新设计和重建的通用物理引擎驱动，集成了各种物理求解器及其耦合到一个统一的框架中。这个核心物理引擎通过一个在上层操作的生成代理框架进一步增强，旨在实现机器人及其他领域的完全**自动化数据生成**。
目前，我们正在开源基础物理引擎和仿真平台。生成框架将在不久的将来发布。

Genesis的构建和持续发展基于以下***长期使命***：

1. **降低使用物理仿真的门槛**，使机器人研究对所有人都可访问。（参见我们的[承诺](https://genesis-world.readthedocs.io/en/latest/user_guide/overview/mission.html)）
2. **将广泛的最先进物理求解器统一到一个框架中**，使用最先进的仿真技术，在虚拟领域中以最高的物理、视觉和感官保真度重现整个物理世界。
3. **最小化人类在收集和生成机器人及其他领域数据上的努力**，让数据飞轮自行旋转。

项目页面：[https://genesis-embodied-ai.github.io/](https://genesis-embodied-ai.github.io/)

## 主要特点

与之前的仿真平台相比，这里我们强调Genesis的几个主要特点：

- 🐍 **100% Python**，前端接口和后端物理引擎均为原生Python开发。
- 👶 **安装简便**，**极其简单**且**用户友好**的API设计。
- 🚀 **并行仿真**，具有***前所未有的速度***：Genesis是**世界上最快的物理引擎**，仿真速度比现有的*GPU加速*机器人仿真器（Isaac Gym/Sim/Lab, Mujoco MJX等）快***10~80倍***（是的，这有点科幻），***且不影响***仿真精度和保真度。
- 💥 一个**统一的框架**，支持各种最先进的物理求解器，建模**广泛的材料**和物理现象。
- 📸 优化性能的照片级真实感光线追踪渲染。
- 📐 **可微性**：Genesis设计为完全兼容可微仿真。目前，我们的MPM求解器和工具求解器是可微的，其他求解器的可微性将很快添加（从刚体仿真开始）。
- ☝🏻 物理精确且可微的**触觉传感器**。
- 🌌 原生支持***[生成仿真](https://arxiv.org/abs/2305.10455)***，允许**语言提示的数据生成**，包括各种模式：*交互场景*、*任务提案*、*奖励*、*资产*、*角色动作*、*策略*、*轨迹*、*相机运动*、*(物理精确的)视频*等。

## 入门指南

### 快速安装

Genesis可通过PyPI获取：

```bash
pip install genesis-world
```

你还需要按照[官方说明](https://pytorch.org/get-started/locally/)安装**PyTorch**。

### 文档

请参考我们的[文档网站](https://genesis-world.readthedocs.io/en/latest/user_guide/index.html)获取详细的安装步骤、教程和API参考。

## 贡献Genesis

Genesis项目的目标是建立一个完全透明、用户友好的生态系统，让来自机器人和计算机图形学领域的贡献者**共同合作，创造一个高效、真实（物理和视觉上）的虚拟世界，用于机器人研究及其他领域**。

我们真诚地欢迎来自社区的*任何形式的贡献*，以使世界对机器人更友好。从**新功能的拉取请求**、**错误报告**，到甚至是让Genesis API更直观的**小建议**，我们都全心全意地感谢！

## 支持

- 请使用Github [Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues)报告错误和提出功能请求。

- 请使用GitHub [Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions)讨论想法和提问。

## 引用

如果你在研究中使用了Genesis，我们将非常感谢你能引用它。我们仍在撰写技术报告，在其公开之前，你可以考虑引用：

```
@software{Genesis,
  author = {Genesis Authors},
  title = {Genesis: A Universal and Generative Physics Engine for Robotics and Beyond},
  month = {December},
  year = {2024},
  url = {https://github.com/Genesis-Embodied-AI/Genesis}
}
```

```{toctree}
:maxdepth: 1

user_guide/index
api_reference/index
roadmap/index

```
