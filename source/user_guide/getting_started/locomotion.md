# 🦿 使用强化学习训练运动策略

Genesis支持并行仿真，使其成为高效训练强化学习（RL）运动策略的理想选择。在本教程中，我们将带您完成一个完整的训练示例，以获得一个基本的运动策略，使Unitree Go2机器人能够行走。使用Genesis，您将能够在不到26秒的时间内训练出一个**可在现实世界中部署的运动策略**（在RTX 4090上进行基准测试）。

**致谢**：本教程的灵感来自并构建于[Legged Gym](https://github.com/leggedrobotics/legged_gym)的几个核心概念之上。

## 环境概述

我们首先创建一个类似gym的环境（go2-env）。

#### 初始化

`__init__`函数通过以下步骤设置仿真环境：

1. **控制频率**。
    仿真以50 Hz运行，与真实机器人的控制频率匹配。为了进一步缩小sim2real的差距，我们还手动模拟了真实机器人上的动作延迟（约20毫秒，一个dt）。
2. **场景创建**。
    创建一个仿真场景，包括机器人和一个静态平面。
3. **PD控制器设置**。
    根据名称识别电机，然后为每个电机设置刚度和阻尼。
4. **奖励注册**。
    根据配置定义的奖励函数被注册以指导策略。这些函数将在“奖励”部分进行解释。
5. **缓冲区初始化**。
    初始化缓冲区以存储环境状态、观察和奖励。

#### 重置

`reset_idx`函数重置指定环境的初始姿态和状态缓冲区。这确保了机器人从预定义的配置开始，对于一致的训练至关重要。

#### 步骤

`step`函数执行动作并返回新的观察和奖励。其工作原理如下：

1. **动作执行**。
    输入动作将被裁剪、重新缩放，并添加到默认电机位置之上。变换后的动作，代表目标关节位置，然后被发送到机器人控制器进行一步执行。
2. **状态更新**。
    机器人状态，如关节位置和速度，被检索并存储在缓冲区中。
3. **终止检查**。
    如果（1）情节长度超过允许的最大值（2）机器人的身体方向显著偏离，环境将被终止。终止的环境会自动重置。
4. **奖励计算**。
5. **观察计算**。
    用于训练的观察包括基础角速度、投影重力、命令、自由度位置、自由度速度和先前的动作。

#### 奖励

奖励函数对于策略指导至关重要。在本示例中，我们使用：

- **tracking_lin_vel**：跟踪线速度命令（xy轴）
- **tracking_ang_vel**：跟踪角速度命令（偏航）
- **lin_vel_z**：惩罚z轴基础线速度
- **action_rate**：惩罚动作变化
- **base_height**：惩罚基础高度偏离目标
- **similar_to_default**：鼓励机器人姿态与默认姿态相似

## 训练

在此阶段，我们已经定义了环境。现在，我们使用rsl-rl的PPO实现来训练策略。请按照以下安装步骤操作：

```
# 安装rsl_rl。
git clone https://github.com/leggedrobotics/rsl_rl
cd rsl_rl && git checkout v1.0.2 && pip install -e .

# 安装tensorboard。
pip install tensorboard
```

安装完成后，通过运行以下命令开始训练：

```
python examples/locomotion/go2_train.py
```

要监控训练过程，请启动TensorBoard：

```
tensorboard --logdir logs
```

您应该会看到类似这样的训练曲线：

```{figure} ../../_static/images/locomotio_curve.png
```

## 评估

最后，让我们展开训练好的策略。运行以下命令：

```
python examples/locomotion/go2_eval.py
```

您应该会看到类似这样的GUI：

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/locomotion_eval.mp4" type="video/mp4">
</video>

如果您恰好有一个真实的Unitree Go2机器人，可以尝试部署该策略。玩得开心！

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/locomotion_real.mp4" type="video/mp4">
</video>
