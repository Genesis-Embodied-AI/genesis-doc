# 🚁 使用强化学习训练无人机悬停策略

Genesis 支持并行仿真，使其成为高效训练强化学习（RL）悬停策略的理想选择。在本教程中，我们将带您完成一个完整的训练示例，以获得一个基本的悬停策略，使无人机能够通过到达随机生成的目标点，并保持稳定的悬停。

这是一个简单且极简的示例，展示了如何在 Genesis 中实现一个非常基础的强化学习训练流程。通过以下示例，您可以快速获得一个可部署到真实无人机上的悬停策略。

**注意**：这*并非*一个全面的hovering policy训练框架。它使用了简化的奖励项以便于您快速上手，并且没有利用 Genesis 在大批量训练(batch size)中的性能，因此这个示例仅用于基本的演示目的。

**致谢**：本教程的灵感来自于[Champion-level drone racing using deep reinforcement learning (Nature 2023)](https://www.nature.com/articles/s41586-023-06419-4.pdf)。

## 环境概述

我们首先创建一个类似 gym 的环境（hover-env）。

### 初始化

`__init__` 函数通过以下步骤设置仿真环境：

1. **控制频率**。
    仿真以 100 Hz 运行，为无人机提供高频控制循环。
2. **场景创建**。
    创建一个仿真场景，包括无人机和一个静态平面。
3. **目标初始化**。
    初始化一个目标点，无人机将尝试到达该目标点。
4. **奖励注册**。
    根据配置定义的奖励函数被注册以指导策略。这些函数将在“奖励”部分中解释。
5. **缓冲区初始化**。
    初始化缓冲区以存储环境状态、观察和奖励。

### 重置

`reset_idx`函数重置指定环境的初始姿态和状态缓冲区。这确保了机器人从预定义的配置开始，对于一致的训练至关重要。

### 步骤

`step`函数执行动作并返回新的观察和奖励。其工作原理如下：

1. **动作执行**。
    输入动作将被裁剪到有效范围，重新缩放，并作为调整应用到默认的悬停螺旋桨转速（RPM）上。
2. **状态更新**。
    无人机的状态，如位置、姿态和速度，被检索并存储在缓冲区中。
3. **终止检查**。
    如果满足以下条件，环境将被终止并重置：
    - 情节长度超过允许的最大值。
    - 无人机的俯仰角或横滚角超过指定阈值。
    - 无人机的位置超过指定边界。
    - 无人机离地面太近。
4. **奖励计算**。
    根据无人机到达目标点和保持稳定性的表现计算奖励。
5. **观察计算**。
    观察值被归一化并返回给策略。用于训练的观察值包括无人机的位置、姿态（四元数）、机体线速度、机体角速度和先前的动作。

### 奖励

奖励函数对于策略指导至关重要。在本示例中，我们使用以下奖励函数来鼓励无人机到达目标点并保持稳定性：

- **target**: 鼓励无人机到达随机生成的目标点。
- **smooth**: 鼓励平滑和受控的动作。
- **yaw**: 鼓励无人机保持稳定的悬停姿态。
- **angular**: 鼓励无人机保持低角速度。
- **crash**: 惩罚无人机碰撞或偏离目标太远。

这些奖励函数结合在一起，为策略提供全面的反馈，指导其实现稳定和准确的悬停行为。

## 训练

在此阶段，我们已经定义了环境。现在，我们使用 rsl-rl 的 PPO 实现来训练无人机悬停策略。请按照以下安装步骤操作：

1. **安装依赖**.
    确保您已安装所有必要的依赖，包括 Genesis 和 `rsl_rl`。

    ```bash
    # 安装 rsl_rl。
    git clone https://github.com/leggedrobotics/rsl_rl
    cd rsl_rl && git checkout v1.0.2 && pip install -e .

    # 安装tensorboard。
    pip install tensorboard
    ```

2. **运行训练脚本**.
    使用提供的训练脚本开始训练策略。

    ```bash
    python hover_train.py -e drone-hovering -B 8192 --max_iterations 300
    ```

    - `-e drone-hovering`：指定实验名称为 "drone-hovering"。
    - `-B 8192`：设置并行训练的环境数量为 8192。
    - `--max_iterations 300`：指定最大训练迭代次数为 300。
    - `-v`: 可选，训练时可视化。

    要监控训练过程，请启动TensorBoard：

    ```bash
    tensorboard --logdir logs
    ```

    您应该会看到类似这样的训练曲线：

    ```{figure} ../../_static/images/hover_curve.png
    ```
    如果开启了训练可视化，您可以看到：
    ```{figure} ../../_static/images/training.gif
    ```

## 评估

要评估训练好的无人机悬停策略，请按照以下步骤操作：

1. **运行评估脚本**。

    使用提供的评估脚本评估训练好的策略。

    ```bash
    python hover_eval.py -e drone-hovering --ckpt 300 --record
    ```

    - `-e drone-hovering`：指定实验名称为 "drone-hovering"。
    - `--ckpt 300`: 从检查点 300 加载训练好的策略。
    - `--record`: 记录评估过程并保存无人机表现的视频。

2. **可视化结果**。
    评估脚本将可视化无人机的表现，并在设置 `--record` 标志时保存视频。

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hover_env.mp4" type="video/mp4">
</video>

通过遵循本教程，您将能够使用 Genesis 训练和评估一个基本的无人机悬停策略。玩得开心，享受过程！