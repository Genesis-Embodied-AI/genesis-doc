# ✍️ Manipulation with Two-Stage Training

This example demonstrates robotic manipulation using a **two-stage training paradigm** that combines **reinforcement learning (RL)** and **imitation learning (IL)**. The central idea is to first train a **privileged teacher policy** using full state information, and then distill that knowledge into a **vision-based student policy** that relies on camera observations and robot states (optional). 

## Environment Overview

The environment is assembled using the following components

* **Robot:** A Franka Panda manipulator with parallel-jaw gripper.
* **Object:** A box with randomized position and orientation.
* **Cameras:** Two stereo RGB cameras (left and right) positioned in front of the scene.
* **Observations:**
  * Privileged state: end-effector pose, object pose.
  * Vision state: stereo RGB images.
* **Actions:** 6-DoF delta end-effector pose (position + orientation).
* **Rewards:** To simplify the reward formulation, we primarily use a **keypoint alignment** reward, which specifies poses between the gripper and object. This is the only reward uesd for aligning the robot's end-effector to a goal pose best for picking up the objects.

## RL Training

In the first stage, we train a teacher policy using **Proximal Policy Optimization (PPO)** from the \[RSL-RL library].

First, install all Python dependencies via `pip`:
```
pip install tensorboard rsl-rl-lib==2.2.4
```
After installation, start training by running:
```
python examples/manipulation/grasp_train.py --stage=rl
```
To monitor the training process, launch TensorBoard:
```
tensorboard --logdir=logs
```
The final training curve for the reward will look like the following
```{figure} ../../_static/images/manipulation_curve.png
```

* **Inputs:** Privileged state observations (no images).
* **Outputs:** End-effector action commands. 
* **Parallel Environments:** Large batches (e.g., 1024–4096 envs) for fast sample throughput.
* **Rewards:** Keypoint alignment ensures the gripper approaches and stabilizes on the object.
* **Outcome:** An MLP policy that can perform the task given groundtruth state informations.

The teacher’s role is to generate reliable demonstration data for the next stage.

## Imitation Learning

The second stage trains a **vision-conditioned student policy** by imitating the RL teacher.

* **Model:**
  * Shared stereo CNN encoder.
  * Feature fusion network.
  * Two heads:
    * **Action head:** Predicts manipulation actions.
    * **Pose head:** Auxiliary task to predict object pose (xyz + quaternion).
* **Training:**
  * Loss = Action MSE + Pose loss (position MSE + quaternion distance).
  * Data collected online with teacher supervision (DAgger-style corrections).
* **Observations:** Stereo RGB images and robot pose.
* **Outcome:** A vision-only policy that generalizes from demonstrations.

This stage bridges the gap between simulation privilege and realistic perception.

After getting a teacher policy using RL, we can start training a student policy (vision-based) by running:
```
python examples/manipulation/grasp_train.py --stage=bc
```

## Evaluation

Policies can be evaluated in simulation with or without visualization:

* **Teacher Policy (MLP):**

  
```python
python examples/manipulation/grasp_eval.py --stage==rl
```

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_rl.mp4" type="video/mp4">
</video>
  
* **Student Policy (CNN+MLP):**

```python
python examples/manipulation/grasp_eval.py --stage=bc --record
```

The vision-based policy observes the environment through a stereo camera which is rendered via Mandrona render.
  
<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/manipulation_stereo.mp4" type="video/mp4">
</video>
  
```python
python examples/manipulation/grasp_eval.py --stage bc
```
* **Logging & Monitoring:**

  * Training metrics logged to TensorBoard (`logs/grasp_rl/` or `logs/grasp_bc/`).
  * Checkpoints saved periodically for both RL and BC stages.

Together, this evaluation validates the two-stage pipeline: a teacher policy that learns efficiently with full information, and a student policy that achieves robust vision-based manipulation through imitation.
