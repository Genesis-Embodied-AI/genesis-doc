# Genesis

```{figure} _static/images/teaser.png
```

## 什么是Genesis？

Genesis是一个面向机器人、具身AI和物理AI应用的通用物理平台。它具备以下核心功能：

1. 全新打造的**通用物理引擎**，能模拟多种材料和物理现象
2. **轻量级**、**高速**、**Python化**且**易用**的机器人仿真平台
3. 强大高效的**照片级真实渲染系统**
4. 基于自然语言生成多模态数据的**生成引擎**

Genesis以全新设计的通用物理引擎为核心，整合了多种物理求解器到统一框架中。在此基础上，我们添加了生成式AI代理层，实现机器人等领域的**全自动数据生成**。目前我们已开源基础物理引擎和仿真平台，生成框架也将很快发布。

Genesis的***长期愿景***包括：

1. **让物理仿真更易用**，使机器人研究惠及所有人（详见我们的[承诺](https://genesis-world.readthedocs.io/en/latest/user_guide/overview/mission.html)）
2. **统一前沿物理求解器**，用最佳仿真技术还原真实物理世界
3. **最小化数据收集成本**，实现自动化数据生成

项目主页：[https://genesis-embodied-ai.github.io/](https://genesis-embodied-ai.github.io/)

## 主要特点

相比其他仿真平台，Genesis具有以下突出优势：

- 🐍 **纯Python实现**，包括前端接口和后端物理引擎
- 👶 **安装便捷**，API设计**简单直观**
- 🚀 **并行仿真**，性能**远超预期**：Genesis是**全球最快的物理引擎**，速度比现有GPU加速仿真器（如Isaac Gym/Sim/Lab、Mujoco MJX等）快**10-80倍**，同时保持高精度
- 💥 **统一框架**支持多种先进物理求解器，可模拟各类材料和物理现象
- 📸 高性能的照片级真实感光追渲染
- 📐 **可微分设计**：目前支持MPM求解器和工具求解器的可微分计算，其他模块（从刚体开始）即将推出
- ☝🏻 物理精确且可微分的**触觉感知**
- 🌌 原生支持[生成式仿真](https://arxiv.org/abs/2305.10455)，通过自然语言生成多种类型数据：场景交互、任务、奖励函数、资产、动作、策略、轨迹、相机运动和物理精确的视频等

## 入门指南

### 快速安装

通过PyPI安装Genesis：

```bash
pip install genesis-world
```

另需按[官方指引](https://pytorch.org/get-started/locally/)安装**PyTorch**。

### 文档

访问[在线文档](https://genesis-world.readthedocs.io/en/latest/user_guide/index.html)获取详细安装教程、使用指南和API文档。

## 参与贡献

Genesis致力于建设开放透明的生态系统，欢迎机器人和计算机图形学领域的专家**共同打造高效真实的虚拟世界**。

我们诚挚欢迎社区各种形式的贡献，包括**功能开发**、**问题报告**和**改进建议**等。

## 获取支持

- 在GitHub [Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues)提交问题和功能建议
- 在GitHub [Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions)参与讨论交流

## 引用

如果您的研究使用了Genesis，请引用：

```bibtex
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
