# 🔗 混合实体

HybridEntity 结合了刚体和软体物理，用于模拟具有刚性骨骼的可变形机器人。

## 概述

混合实体耦合了：
- **刚体组件**：骨骼/结构（来自 URDF）
- **软体组件**：可变形皮肤（基于 MPM）

用例：软体夹爪、可变形机器人、柔顺机械臂。

## 创建混合实体

```python
import genesis as gs

gs.init()
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=3e-3, substeps=10),
    mpm_options=gs.options.MPMOptions(
        lower_bound=(0, 0, -0.2),
        upper_bound=(1, 1, 1),
    ),
)

robot = scene.add_entity(
    morph=gs.morphs.URDF(
        file="robot.urdf",
        pos=(0.5, 0.5, 0.3),
        fixed=True,
    ),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.05,
        damping=1000.0,
    ),
)

scene.build()
```

## 混合材质选项

```python
gs.materials.Hybrid(
    material_rigid=gs.materials.Rigid(),     # 刚体材质
    material_soft=gs.materials.MPM.Muscle(), # 软体材质（仅 MPM）
    thickness=0.05,                          # 软皮肤厚度
    damping=1000.0,                          # 速度阻尼
    soft_dv_coef=0.01,                       # 刚体→软体速度传递
)
```

## 控制

控制使用刚体骨骼的 DOF：

```python
import numpy as np

for step in range(1000):
    # 正弦关节控制
    target_vel = [np.sin(step * 0.01)] * robot.n_dofs
    robot.control_dofs_velocity(target_vel)
    scene.step()
```

## 访问组件

```python
robot.part_rigid   # RigidEntity（骨骼）
robot.part_soft    # MPMEntity（皮肤）
robot.n_dofs       # DOF 数量

# 状态访问
robot.get_dofs_position()
robot.get_dofs_velocity()
```

## 示例：软体夹爪

```python
gripper = scene.add_entity(
    morph=gs.morphs.URDF(file="gripper.urdf", fixed=True),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(gravity_compensation=1.0),
        material_soft=gs.materials.MPM.Muscle(E=1e4, nu=0.45),
        thickness=0.02,
        damping=100.0,
    ),
)

# 添加要抓取的对象
ball = scene.add_entity(
    morph=gs.morphs.Sphere(pos=(0.5, 0.5, 0.1), radius=0.05),
)

scene.build()

# 闭合夹爪
for step in range(500):
    gripper.control_dofs_position([0.5] * gripper.n_dofs)
    scene.step()
```

## 从网格创建（自动骨架化）

从任意网格创建混合实体：

```python
creature = scene.add_entity(
    morph=gs.morphs.Mesh(file="creature.obj", scale=0.1),
    material=gs.materials.Hybrid(
        material_rigid=gs.materials.Rigid(),
        material_soft=gs.materials.MPM.Muscle(E=1e4),
    ),
)
```

Genesis 自动执行：
1. 通过骨架化从网格提取骨骼
2. 从骨骼创建刚体
3. 将软体粒子映射到骨骼连杆

## 注意事项

- 软体材质必须是基于 MPM 的（`gs.materials.MPM.*`）
- 较高的 `damping` 可减少振荡
- 需要具有适当边界的 `mpm_options`
