# `RigidJoint`

`RigidJoint` 用于定义两个 RigidLink 之间的约束关系，限制它们的相对运动。关节可以有不同的类型，如铰链关节、球关节等，每种类型提供不同的自由度限制。

## 功能说明

`RigidJoint` 类提供了以下主要功能：

- 定义两个刚体链接之间的约束关系
- 支持多种关节类型（铰链、球关节、棱柱、固定等）
- 提供关节的位置和角度控制
- 允许设置关节的物理参数（刚度、阻尼、摩擦等）
- 支持关节的运动限制（角度范围、位移范围等）

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 关节在引擎中的全局索引 |
| `idx_local` | `int` | 关节在实体中的局部索引 |
| `uid` | `int` | 关节的唯一标识符 |
| `name` | `str` | 关节的名称 |
| `type` | `str` | 关节类型（hinge, ball, prismatic, fixed等） |
| `link` | `RigidLink` | 关联的主要链接 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `pos` | `list` | 关节位置 [x, y, z] |
| `quat` | `list` | 关节姿态四元数 [w, x, y, z] |
| `axis` | `list` | 关节轴向量 [x, y, z]（用于铰链和棱柱关节） |
| `n_dofs` | `int` | 关节的自由度数量 |
| `n_qs` | `int` | 关节的状态变量数量 |
| `dofs_idx` | `list` | 关节自由度在全局索引中的位置 |
| `dofs_idx_local` | `list` | 关节自由度在实体中的局部索引 |
| `dofs_kp` | `list` | 位置控制增益 |
| `dofs_kv` | `list` | 速度控制增益 |
| `dofs_stiffness` | `list` | 刚度参数 |
| `dofs_damping` | `list` | 阻尼参数 |
| `dofs_invweight` | `list` | 逆权重 |
| `dofs_frictionloss` | `list` | 摩擦损失 |
| `dofs_limit` | `list` | 运动限制 |
| `dofs_force_range` | `list` | 力范围限制 |
| `dofs_motion_ang` | `list` | 运动角度 |
| `dofs_motion_vel` | `list` | 运动速度 |
| `sol_params` | `list` | 求解器参数 |
| `is_built` | `bool` | 关节是否已构建完成 |

## 代码示例

```python
import genesis
from genesis import World, RigidEntity

# 创建一个新的世界
world = World()

# 创建一个包含关节的刚体实体（双摆）
double_pendulum = RigidEntity(
    world=world,
    name="double_pendulum",
    link_params=[
        {
            "name": "upper_arm",
            "geoms": [
                {
                    "type": "cylinder",
                    "size": [0.05, 1.0],
                    "pos": [0, 0, 0.5],
                    "material": "default"
                }
            ],
            "inertial_mass": 1.0
        },
        {
            "name": "lower_arm",
            "geoms": [
                {
                    "type": "cylinder",
                    "size": [0.05, 1.0],
                    "pos": [0, 0, 0.5],
                    "material": "default"
                }
            ],
            "inertial_mass": 1.0
        }
    ],
    joint_params=[
        {
            "name": "shoulder",
            "type": "hinge",
            "link_idx1": 0,
            "pos": [0, 0, 0],  # 肩关节位置
            "axis": [0, 1, 0],  # 绕Y轴旋转
            "dofs_kp": [1000.0],  # 位置控制增益
            "dofs_kv": [50.0],    # 速度控制增益
            "dofs_limit": [[-1.57, 1.57]]  # 角度限制（-90度到90度）
        },
        {
            "name": "elbow",
            "type": "hinge",
            "link_idx1": 0,
            "link_idx2": 1,
            "pos": [0, 0, 1.0],  # 肘关节位置
            "axis": [0, 1, 0],   # 绕Y轴旋转
            "dofs_kp": [800.0],   # 位置控制增益
            "dofs_kv": [40.0],    # 速度控制增益
            "dofs_limit": [[0, 3.14]]  # 角度限制（0度到180度）
        }
    ]
)

# 初始化世界
world.init()

# 获取关节信息
shoulder_joint = double_pendulum.joints[0]
elbow_joint = double_pendulum.joints[1]

# 打印关节信息
print(f"Shoulder joint type: {shoulder_joint.type}")
print(f"Shoulder joint position: {shoulder_joint.pos}")
print(f"Shoulder joint axis: {shoulder_joint.axis}")
print(f"Elbow joint type: {elbow_joint.type}")
print(f"Elbow joint position: {elbow_joint.pos}")
print(f"Elbow joint axis: {elbow_joint.axis}")

# 运行模拟
for _ in range(200):
    world.step()
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_joint.RigidJoint
    :members:
    :show-inheritance:
    :undoc-members:
```
