# `RigidGeom`

`RigidGeom` 用于定义刚体链接的碰撞几何形状，主要用于碰撞检测和碰撞响应。每个 RigidLink 可以包含多个 RigidGeom，它们共同定义了刚体的碰撞边界。

## 功能说明

`RigidGeom` 类提供了以下主要功能：

- 定义碰撞几何形状的类型和参数
- 设置几何形状的位置和姿态
- 管理碰撞材质属性（摩擦、 restitution 等）
- 提供碰撞检测所需的几何信息
- 支持多种几何形状类型（盒子、球体、圆柱体、胶囊体、网格等）

## 主要属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `idx` | `int` | 几何形状在引擎中的全局索引 |
| `idx_local` | `int` | 几何形状在链接中的局部索引 |
| `uid` | `int` | 几何形状的唯一标识符 |
| `name` | `str` | 几何形状的名称 |
| `type` | `str` | 几何形状类型（box, sphere, cylinder, capsule, mesh等） |
| `link` | `RigidLink` | 所属的刚体链接 |
| `entity` | `RigidEntity` | 所属的刚体实体 |
| `pos` | `list` | 几何形状在链接坐标系中的位置 [x, y, z] |
| `quat` | `list` | 几何形状在链接坐标系中的姿态四元数 [w, x, y, z] |
| `size` | `list` | 几何形状的尺寸参数，根据类型不同而变化 |
| `material` | `str` | 碰撞材质名称 |
| `friction` | `float` | 摩擦系数 |
| `restitution` | `float` |  restitution 系数（弹性） |
| `thickness` | `float` | 几何形状的厚度（用于某些类型） |
| `mesh` | `object` | 网格对象（如果类型为mesh） |
| `n_verts` | `int` | 顶点数量（如果类型为mesh） |
| `n_faces` | `int` | 面数量（如果类型为mesh） |
| `n_edges` | `int` | 边数量（如果类型为mesh） |
| `vert_start` | `int` | 顶点起始索引（如果类型为mesh） |
| `vert_end` | `int` | 顶点结束索引（如果类型为mesh） |
| `face_start` | `int` | 面起始索引（如果类型为mesh） |
| `face_end` | `int` | 面结束索引（如果类型为mesh） |
| `is_built` | `bool` | 几何形状是否已构建完成 |

## 代码示例

```python
import genesis
from genesis import World, RigidEntity

# 创建一个新的世界
world = World()

# 创建一个包含多种碰撞几何形状的刚体实体
robot_arm = RigidEntity(
    world=world,
    name="robot_arm",
    link_params=[
        {
            "name": "base",
            "geoms": [
                {
                    "type": "box",
                    "size": [0.5, 0.5, 0.2],
                    "pos": [0, 0, 0.1],
                    "material": "default",
                    "friction": 0.8,
                    "restitution": 0.2
                }
            ],
            "is_free": False  # 固定基座
        },
        {
            "name": "upper_arm",
            "geoms": [
                {
                    "type": "cylinder",
                    "size": [0.05, 0.8],
                    "pos": [0, 0, 0.4],
                    "material": "default"
                },
                {
                    "type": "sphere",
                    "size": [0.08],
                    "pos": [0, 0, 0],
                    "material": "default"
                },
                {
                    "type": "sphere",
                    "size": [0.08],
                    "pos": [0, 0, 0.8],
                    "material": "default"
                }
            ]
        },
        {
            "name": "lower_arm",
            "geoms": [
                {
                    "type": "capsule",
                    "size": [0.05, 0.6],
                    "pos": [0, 0, 0.3],
                    "material": "default"
                }
            ]
        }
    ],
    joint_params=[
        {
            "name": "shoulder",
            "type": "hinge",
            "link_idx1": 0,
            "link_idx2": 1,
            "pos": [0, 0, 0.2],
            "axis": [0, 1, 0]
        },
        {
            "name": "elbow",
            "type": "hinge",
            "link_idx1": 1,
            "link_idx2": 2,
            "pos": [0, 0, 0.8],
            "axis": [0, 1, 0]
        }
    ]
)

# 初始化世界
world.init()

# 获取几何形状信息
base_link = robot_arm.links[0]
base_box = base_link.geoms[0]

upper_arm = robot_arm.links[1]
cylinder_geom = upper_arm.geoms[0]

# 打印几何形状信息
print(f"Base geom type: {base_box.type}")
print(f"Base geom size: {base_box.size}")
print(f"Base geom position: {base_box.pos}")
print(f"Upper arm cylinder size: {cylinder_geom.size}")
print(f"Upper arm cylinder friction: {cylinder_geom.friction}")

# 运行模拟
for _ in range(100):
    world.step()
```

```{eval-rst}
.. autoclass:: genesis.engine.entities.rigid_entity.rigid_geom.RigidGeom
    :members:
    :show-inheritance:
    :undoc-members:
```
