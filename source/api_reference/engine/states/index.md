# States

Genesis 中的 States 保存物理仿真的运行时数据，包括位置、速度、力以及其他 solver 特定的变量。

## 概览

每个 solver 维护自己的 state：

- **RigidState**: Link 位姿、joint 位置/速度
- **MPMState**: 粒子位置、速度、变形梯度
- **FEMState**: 节点位置、速度
- **PBDState**: 粒子位置、速度
- **SPHState**: 粒子位置、速度、密度

## 访问 State

States 通过 entities 或 simulator 访问：

```python
import genesis as gs

gs.init()
scene = gs.Scene()
robot = scene.add_entity(gs.morphs.URDF(file="robot.urdf"))
scene.build()

# 通过 entity 访问
positions = robot.get_qpos()      # Joint 位置
velocities = robot.get_qvel()     # Joint 速度
link_pos = robot.get_link("ee").get_pos()

# 完整 state 访问（高级）
rigid_solver = scene.sim.rigid_solver
# ... 直接访问 solver state
```

## 并行环境的 State

使用 `n_envs > 1` 时，states 是批量的：

```python
scene.build(n_envs=16)

# 批量 state 访问
positions = robot.get_qpos()  # Shape: (n_envs, n_dofs)

# 按环境访问
positions = robot.get_qpos(envs_idx=[0, 5, 10])
```

## State 管理

### 保存 State

```python
state = scene.get_state()
```

### 恢复 State

```python
scene.set_state(state)
```

### 重置

```python
scene.reset()  # 重置所有环境
scene.reset(envs_idx=[0, 1, 2])  # 重置特定环境
```

## 梯度追踪

用于可微分仿真：

```python
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        requires_grad=True,
    ),
)

# States 现在追踪梯度
scene.step()
loss = compute_loss(robot.get_qpos())
loss.backward()
```

## 另请参阅

- {doc}`/api_reference/differentiation/index` - 可微分仿真
- {doc}`/api_reference/scene/scene` - Scene state 方法
