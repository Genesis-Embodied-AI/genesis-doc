# 🚁 Training Drone Hovering Policies with RL

Genesis supports parallel simulation, making it ideal for training reinforcement learning (RL) drone hovering policies efficiently. In this tutorial, we will walk you through a complete training example for obtaining a basic hovering policy that enables a drone to maintain a stable hover position by reaching randomly generated target points.

This is a simple and minimal example that demonstrates a very basic RL training pipeline in Genesis, and with the following example you will be able to obtain a drone hovering policy that's deployable to a real drone very quickly.

**Note**: This is *NOT* a comprehensive drone hovering policy training pipeline. It uses simplified reward terms to get you started easily, and does not exploit Genesis's speed on big batch sizes, so it only serves basic demonstration purposes.

**Acknowledgement**: This tutorial is inspired by [Champion-level drone racing using deep reinforcement learning (Nature 2023)](https://www.nature.com/articles/s41586-023-06419-4.pdf).

## Environment Overview
We start by creating a gym-style environment (hover-env).

#### Initialize
The `__init__` function sets up the simulation environment with the following steps:
1. **Control Frequency**.
    The simulation runs at 100 Hz, providing a high-frequency control loop for the drone.
2. **Scene Creation**.
    A simulation scene is created, including the drone and a static plane.
3. **Target Initialization**.
    A random target point is initialized, which the drone will attempt to reach.
4. **Reward Registration**.
    Reward functions, defined in the configuration, are registered to guide the policy. These functions will be explained in the "Reward" section.
5. **Buffer Initialization**.
    Buffers are initialized to store environment states, observations, and rewards.

#### Reset
The `reset_idx` function resets the initial pose and state buffers of the specified environments. This ensures robots start from predefined configurations, crucial for consistent training.

#### Step
The `step` function updates the environment state based on the actions taken by the policy. It includes the following steps:
1. **Action Execution**.
    The input action will be clipped to a valid range, rescaled, and applied as adjustments to the default hover propeller RPMs.
2. **State Update**.
    Drone states, such as position, attitude, and velocities, are retrieved and stored in buffers.
3. **Termination Checks**.
    Terminated environments are reset automatically. Environments are terminated if
    - Episode length exceeds the maximum allowed.
    - The drone's pitch or roll angle exceeds a specified threshold.
    - The drone's position exceeds specified boundaries.
    - The drone is too close to the ground.
4. **Reward Computation**.
    Rewards are calculated based on the drone's performance in reaching the target point and maintaining stability.
5. **Observation Computation**.
    Observations are normalized and returned to the policy. Observations used for training include drone's position, attitude (quaternion), body linear velocity, body angular velocity and previous actions.

#### Reward
In this example, we use the following reward functions to encourage the drone to reach the target point and maintain stability:
- **target**: Encourages the drone to reach the randomly generated target points.
- **smooth**: Encourages smooth actions and bridge the sim-to-real gap.
- **yaw**: Encourages the drone to maintain a stable hover yaw.
- **angular**: Encourages the drone to maintain low angular velocities.
- **crash**: Penalizes the drone for crashing or deviating too far from the target.

These reward functions are combined to provide comprehensive feedback to the policy, guiding it to achieve stable and accurate hovering behavior.

## Training
At this stage, we have defined the environments. To train the drone hovering policy using PPO, follow these steps:
1. **Install Dependencies**.
    First, ensure you have Genesis installed, then add all required Python dependencies using `pip`:
    ```bash
    pip install --upgrade pip
    pip install tensorboard rsl-rl-lib==2.2.4
    ```
2. **Run Training Script**.
    Use the provided training script to start training the policy.
    ```bash
    python hover_train.py -e drone-hovering -B 8192 --max_iterations 301
    ```
    - `-e drone-hovering`: Specifies the experiment name as "drone-hovering".
    - `-B 8192`: Sets the number of environments to 8192 for parallel training.
    - `--max_iterations 301`: Specifies the maximum number of training iterations to 301.
    - `-v`: Optional. Enables training with visualization.

    To monitor the training process, launch TensorBoard:
    ```bash
    tensorboard --logdir logs
    ```
    You should see a training curve similar to this:
    ```{figure} ../../_static/images/hover_curve.png
    ```
    When training with visualization enabled, you will see:
    ```{figure} ../../_static/images/training.gif
    ```

## Evaluation
To evaluate the trained drone hovering policy, follow these steps:
1. **Run Evaluation Script**.
    Use the provided evaluation script to evaluate the trained policy.
    ```bash
    python hover_eval.py -e drone-hovering --ckpt 300 --record
    ```
    - `-e drone-hovering`: Specifies the experiment name as "drone-hovering".
    - `--ckpt 300`: Loads the trained policy from checkpoint 300.
    - `--record`: Records the evaluation and saves a video of the drone's performance.
2. **Visualize Results**.
    The evaluation script will visualize the drone's performance and save a video if the `--record` flag is set.

<video preload="auto" controls="True" width="100%">
<source src="https://github.com/Genesis-Embodied-AI/genesis-doc/raw/main/source/_static/videos/hover_env.mp4" type="video/mp4">
</video>

By following this tutorial, you'll be able to train and evaluate a basic drone hovering policy using Genesis. Have fun and enjoy!