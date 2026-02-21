# Genesis

```{figure} _static/images/teaser.png
```

[![GitHub Repo stars](https://img.shields.io/github/stars/Genesis-Embodied-AI/Genesis?style=plastic&logo=GitHub&logoSize=auto)](https://github.com/Genesis-Embodied-AI/Genesis)
[![PyPI version](https://badge.fury.io/py/genesis-world.svg?icon=si%3Apython)](https://pypi.org/project/genesis-world/)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fgenesis-embodied-ai.github.io%2F)](https://genesis-embodied-ai.github.io/)
[![Discord](https://img.shields.io/discord/1322086972302430269?logo=discord)](https://discord.gg/nukCuhB47p)
<a href="https://drive.google.com/uc?export=view&id=1ZS9nnbQ-t1IwkzJlENBYqYIIOOZhXuBZ"><img src="https://img.shields.io/badge/WeChat-07C160?style=for-the-badge&logo=wechat&logoColor=white" height="20" style="display:inline"></a>


## Genesis 是什么？

Genesis 是一个为通用*机器人/具身智能/物理 AI*应用设计的物理平台。它同时包含以下几个方面：

1. 一个从零开始重新构建的**通用物理引擎**，能够仿真各种材料和物理现象。
2. 一个**轻量级**、**超高速**、**Pythonic**且**用户友好**的机器人仿真平台。
3. 一个强大且快速的**照片级真实感渲染系统**。
4. 一个**生成式数据引擎**，可将用户提示的自然语言描述转换为各种模态的数据。

Genesis 基于从零开始重新设计和构建的通用物理引擎，将各种物理求解器及其耦合整合到一个统一的框架中。这个核心物理引擎进一步由上层运行的生成式代理框架增强，旨在实现机器人及其他领域完全**自动化的数据生成**。
目前，我们正在开源底层物理引擎和仿真平台。生成式框架将在近期发布。

Genesis 的构建和持续演进遵循以下***长期使命***：

1. **降低**使用物理仿真的门槛，让机器人研究对每个人都可及。（参见我们的[承诺](https://genesis-world.readthedocs.io/en/latest/user_guide/overview/mission.html)）
2. **将广泛的最先进物理求解器统一**到一个框架中，使用最先进的仿真技术，以最高的物理、视觉和感官保真度在虚拟世界中重现整个物理世界。
3. **最小化**机器人及其他领域数据收集和生成的人力投入，让数据飞轮自行运转。

## 核心特性

与以往的仿真平台相比，以下是 Genesis 的几个核心特性：

- 🐍 **100% Python**，前端接口和后端物理引擎都原生使用 Python 开发。
- 👶 **轻松安装**，API 设计**极其简单**且**用户友好**。
- 🚀 **并行仿真**带来***前所未有的速度***：Genesis 是**世界上最快的物理引擎**，仿真速度比现有的*GPU 加速*机器人仿真器（Isaac Gym/Sim/Lab、Mujoco MJX 等）快***10~80 倍***（是的，这有点科幻），同时***不妥协***仿真精度和保真度。
- 💥 **统一**框架支持各种最先进的物理求解器，建模**广泛的材料**和物理现象。
- 📸 优化的照片级真实感光线追踪渲染。
- 📐 **可微分性**：Genesis 设计为与可微分仿真完全兼容。目前，我们的 MPM 求解器和工具求解器是可微分的，其他求解器的可微分性将很快添加（从刚体仿真开始）。
- ☝🏻 物理精确且可微分的**触觉传感器**。
- 🌌 原生支持[生成式仿真](https://arxiv.org/abs/2305.10455)，允许**语言提示的数据生成**，包括各种模态：*交互式场景*、*任务提案*、*奖励*、*资产*、*角色动作*、*策略*、*轨迹*、*相机运动*、*（物理精确的）视频*等。

## 快速开始

### 快速安装

Genesis 可通过 PyPI 获取：

```bash
pip install genesis-world
```

您还需要按照[官方说明](https://pytorch.org/get-started/locally/)安装 **PyTorch**。

### 文档

请参阅我们的[文档站点](https://genesis.osaerialrobot.top/user_guide/index.html)了解详细的安装步骤、教程和 API 参考。

## 为 Genesis 贡献

Genesis 项目的目标是构建一个完全透明、用户友好的生态系统，让来自机器人和计算机图形学领域的贡献者能够**齐聚一堂，协作创建一个高效率、真实（包括物理和视觉）的虚拟世界，用于机器人研究及其他领域**。

我们诚挚欢迎社区以*任何形式*做出贡献，让世界成为机器人更好的地方。从**新功能的 pull request**、**bug 报告**，到哪怕是让 Genesis API 更直观的微小**建议**，都衷心感谢！

## 支持

- 请使用 Github [Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues)提交 bug 报告和功能请求。

- 请使用 GitHub [Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions)讨论想法和提问。

## 引用

如果您在您的研究中使用了 Genesis，我们将非常感谢您能引用它。我们仍在撰写技术报告，在它公开之前，您可以考虑引用：

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
roadmap/index

```
