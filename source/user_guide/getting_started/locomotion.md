# 🦿 Training Locomotion Policies with RL

Genesis supports parallel simulation, making it ideal for training reinforcement learning (RL) locomotion policies efficiently. In this tutorial, we will walk you through a complete training example for obtaining a basic locomotion policy that enables a Unitree Go2 Robot to walk.

This is a simple and minimal example that demonstrates a very basic RL training pipeline in Genesis, and with the following example you will be able to obtain a quadruped locomotion policy that's deployable to a real robot very quickly.

**Note**: This is *NOT* a comprehensive locomotion policy training pipeline. It uses simplified reward terms to get you started easily, and does not exploit Genesis's speed on big batchsizes, so it only serves basic demonstration purposes.

**Acknowledgement**: This tutorial is inspired by and builds several core concepts from [Legged Gym](https://github.com/leggedrobotics/legged_gym).

## Environment Overview
We start by creating a gym-style environment (go2-env).
#### Initialize

The `__init__` function sets up the simulation environment with the following steps:
1. **Control Frequency**.
    The simulation runs at 50 Hz, matching the real robot's control frequency. To further bridge sim2real gap, we also manually simulate the action latecy (~20ms, one dt) shown on the real robot.
2. **Scene Creation**.
    A simulation scene is created, including the robot and a static plane.
3. **PD Controller Setup**.
    Motors are first identified based on their names. Stiffness and damping are then set for each motor.
4. **Reward Registration**.
    Reward functions, defined in the configuration, are registered to guide the policy. These functions will be explained in the "Reward" section.
5. **Buffer Initialization**.
    Buffers are initialized to store environment states, observations, and rewards

#### Reset
The `reset_idx` function resets the initial pose and state buffers of the specified environments. This ensures robots start from predefined configurations, crucial for consistent training.

#### Step
The `step` function takes the action for execution and returns new observations and rewards. Here is how it works:
1. **Action Execution**.
    The input action will be clipped, rescaled, and added on top of default motor positions. The transformed action, representing target joint positions, will then be sent to the robot controller for one-step execution.
2. **State Updates**.
    Robot states, such as joint positions and velocities, are retrieved and stored in buffers.
3. **Termination Checks**.
    Environments are terminated if (1) Episode length exceeds the maximum allowed (2) The robot’s body orientation deviates significantly. Terminated environments are reset automatically.
4. **Reward Computation**.
5. **Observation Computation**.
    Observation used for training includes base angular velocity, projected gravity, commands, dof position, dof velocity, and previous actions.


#### Reward
Reward functions are critical for policy guidance. In this example, we use:
- **tracking_lin_vel**: Tracking of linear velocity commands (xy axes)
- **tracking_ang_vel**: Tracking of angular velocity commands (yaw)
- **lin_vel_z**: Penalize z axis base linear velocity
- **action_rate**: Penalize changes in actions
- **base_height**: Penalize base height away from target
- **similar_to_default**: Encourage the robot pose to be similar to the default pose

## Training
At this stage, we have defined the environments. Now, we use the PPO implementation from rsl-rl to train the policy. First, install all Python dependencies via `pip`:
```
pip install tensorboard rsl-rl-lib==2.2.4
```
After installation, start training by running:
```
python examples/locomotion/go2_train.py
```
To monitor the training process, launch TensorBoard:
```
tensorboard --logdir logs
```
You should see a training curve similar to this:
```{figure} ../../_static/images/locomotio_curve.png
```

## Evaluation
Finally, let's roll out the trained policy. Run the following command:
```
python examples/locomotion/go2_eval.py
```
You should see a GUI similar to this:

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/locomotion_eval.mp4" type="video/mp4">
</video>

If you happen to have a real Unitree Go2 robot by your side, you can try to deploy the policy. Have fun!

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/locomotion_real.mp4" type="video/mp4">
</video>
