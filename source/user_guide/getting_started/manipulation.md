# ✍️ 两阶段训练的机器人操作

本示例演示使用**两阶段训练范式**的机器人操作，结合了**强化学习（RL）**和**模仿学习（IL）**。核心思想是首先使用完整状态信息训练一个**特权教师策略**，然后将该知识蒸馏到一个**基于视觉的学生策略**中，该策略依赖于相机观测（以及可选的机器人本体感知）。
这种方法能够在模拟中实现高效学习，同时缩小向真实世界部署的差距，因为在真实世界中特权状态是不可用的。

---

## 环境概述

操作环境由以下元素组成：

* **机器人:** 一个带平行夹爪的 7-DoF Franka Panda 机械臂。
* **物体:** 一个具有随机初始位置和方向的盒子，确保多样化的训练场景。
* **相机:** 两个面向操作场景的立体 RGB 相机（左和右）。这里，我们使用 [Madrona Engine](https://madrona-engine.github.io/) 进行批量渲染。
* **观测值：**

  * **特权状态:** 末端执行器位姿和物体位姿（仅在教师训练期间使用）。
  * **视觉状态:** 立体 RGB 图像（由学生策略使用）。
* **动作:** 6-DoF 增量末端执行器位姿命令（3D 位置 + 方向）。
* **奖励:** 使用**关键点对齐**奖励。这定义了夹爪和物体之间的参考关键点，鼓励夹爪对齐到可抓取姿态。

  * 这种表述避免了密集的塑形项，直接编码任务成功。
  * 策略学习到达目标只需要这个奖励。

---

## RL 训练（第一阶段：教师策略）

在第一阶段，我们使用 [RSL-RL 库](https://github.com/leggedrobotics/rsl_rl) 中的 **近端策略优化（PPO）** 训练教师策略。

**设置：**

```bash
pip install tensorboard rsl-rl-lib==2.2.4
```

**训练：**

```bash
python examples/manipulation/grasp_train.py --stage=rl
```

**监控：**

```bash
tensorboard --logdir=logs
```

如果训练成功，奖励学习曲线如下所示：

```{figure} ../../_static/images/manipulation_curve.png
```

**关键细节：**

* **输入：** 特权状态（无图像）。
* **输出：** 末端执行器动作命令。
* **并行化：** 大批量向量化的 rollout（例如，1024-4096 个环境）以实现快速吞吐。
* **奖励设计：** 关键点对齐足以产生一致的抓取行为。
* **结果：** 一个轻量级的 MLP 策略，在给定真实状态信息的情况下学习稳定抓取。

教师策略作为下一阶段的演示源。

---

## 模仿学习（第二阶段：学生策略）

第二阶段训练一个**视觉条件化的学生策略**，该策略模仿 RL 教师。

**架构：**

* **编码器:** 共享的立体 CNN 编码器提取视觉特征。
* **融合网络:** 将图像特征与可选的机器人本体感知合并。
* **头：**
  * **动作头:** 预测 6-DoF 操作动作。
  * **位姿头:** 预测物体位姿（xyz + 四元数）的辅助任务。

**训练目标：**

* **损失：**
  * 动作 MSE（学生 vs 教师）。
  * 位姿损失 = 位置 MSE + 四元数距离。
* **数据收集:** 教师提供在线监督，可选择使用 **DAgger 风格的修正**来减轻协变量偏移。

**结果：** 一个仅视觉的策略，能够在不访问特权状态的情况下泛化抓取行为。

**运行训练：**

```bash
python examples/manipulation/grasp_train.py --stage=bc
```

---

## 评估

教师策略和学生策略都可以在模拟中进行评估（有或没有可视化）。

* **教师策略（MLP）：**

```bash
python examples/manipulation/grasp_eval.py --stage=rl
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_rl.mp4" type="video/mp4">
</video>

* **学生策略（CNN+MLP）：**

```bash
python examples/manipulation/grasp_eval.py --stage=bc --record
```

学生通过 Madrona 渲染的立体相机观察环境。<video preload="auto" controls="True" width="100%"> <source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_stereo.mp4" type="video/mp4"> </video>


**日志与监控：**

* 指标记录在 TensorBoard 中（`logs/grasp_rl/` 或 `logs/grasp_bc/`）。
* RL 和 BC 阶段都有定期检查点。

---

## 总结

这个两阶段流程说明了一个实用的机器人操作策略：

1. **教师策略（RL）：** 使用完整信息进行高效学习。
2. **学生策略（IL）：** 从演示中蒸馏出的基于视觉的控制。

结果是一个在训练中样本高效且对真实感知输入具有鲁棒性的策略。

