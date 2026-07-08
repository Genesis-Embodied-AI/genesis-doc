# Examples

These are the end-to-end reinforcement learning (RL) training examples that ship with Genesis World. Each one is a complete pipeline: a gym-style environment, its reward terms, and the loop that trains a policy for one task. Together they show how Genesis World's parallel simulation turns into a working policy on a concrete robot.

Read them in any order. If you are new to policy training here, start with locomotion — it is the smallest of the three:

- **{doc}`Locomotion <locomotion>`:** train a Unitree Go2 quadruped to walk with PPO.
- **{doc}`Drone hovering <hover_env>`:** train a drone to reach and hold a target position with PPO.
- **{doc}`Manipulation <manipulation>`:** train a Franka arm to pick and place with a two-stage pipeline that combines RL and imitation learning.

```{toctree}
:hidden:
:maxdepth: 1

locomotion
hover_env
manipulation
```
