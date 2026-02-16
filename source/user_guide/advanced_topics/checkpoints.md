# 💾 检查点 (Checkpoints)

Genesis 提供状态保存/加载功能，用于训练恢复和回合重置。

## 基本保存/加载

```python
import genesis as gs

scene = gs.Scene()
robot = scene.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene.build()

# 仿真
for _ in range(100):
    scene.step()

# 保存检查点
scene.save_checkpoint("checkpoint.pkl")

# 在新场景中加载
scene2 = gs.Scene()
robot2 = scene2.add_entity(gs.morphs.MJCF(file="franka.xml"))
scene2.build()
scene2.load_checkpoint("checkpoint.pkl")
```

## 状态对象

```python
# 获取当前状态（内存中）
state = scene.get_state()

# 重置到初始状态
scene.reset()

# 重置到自定义状态
scene.reset(state=state)
```

## RL 回合重置

```python
scene.build(n_envs=N)

# 快照初始状态
init_state = scene.get_state()

for episode in range(num_episodes):
    scene.reset(state=init_state)

    for step in range(episode_length):
        scene.step()
        obs, reward, done = get_observations()

        # 重置回合结束的环境
        if done.any():
            done_envs = torch.where(done)[0].tolist()
            scene.reset(state=init_state, envs_idx=done_envs)
```

## 选择性环境重置

```python
scene.build(n_envs=16)

# 重置所有环境
scene.reset()

# 重置特定环境
scene.reset(envs_idx=[0, 2, 5])

# 为特定环境重置自定义状态
scene.reset(state=init_state, envs_idx=[1, 3, 7])
```

## 状态内容

`SimState` 对象包含：

| 求解器 | 状态变量 |
|--------|-----------------|
| Rigid | `qpos`, `dofs_vel`, `links_pos`, `links_quat` |
| MPM | `pos`, `vel`, `C`, `F`, `Jp`, `active` |
| SPH | `pos`, `vel`, `active` |
| PBD | `pos`, `vel`, `free` |
| FEM | `pos`, `vel`, `active` |

## 检查点文件格式

检查点是 pickled 字典：

```python
{
    "timestamp": time.time(),
    "step_index": scene.t,
    "arrays": {  # 按键为求解器/字段的 Numpy 数组
        "RigidSolver.qpos": np.array(...),
        "MPMSolver.pos": np.array(...),
        ...
    }
}
```

## 传输序列化

```python
# 使状态可序列化（从图中分离）
state = scene.get_state()
state_serializable = state.serializable()

# 现在可以安全地 pickle
import pickle
with open("state.pkl", "wb") as f:
    pickle.dump(state_serializable, f)
```

## 重要说明

- 检查点需要兼容的场景配置（相同的实体、求解器选项）
- 32 位精度在保存/加载之间可能损失 ~2e-6 的精度
- 使用 `envs_idx` 参数进行高效的部分重置
- `scene.t` 存储仿真步数
